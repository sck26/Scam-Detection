"""Train/evaluate a real-message SMS spam baseline with an FPR budget.

Uses original human-labeled ham/spam annotations. Does not create LLM labels.
Caution: spam is NOT equivalent to fraud; evaluate phishing separately.

Usage from ml/ after `pip install -e .`:
  python -m scamguard.realworld_sms train --input data/raw/spam.csv \
      --output models/realworld_sms.joblib --max-fpr 0.005
  python -m scamguard.realworld_sms predict --model models/realworld_sms.joblib \
      'Your verification code is 123456. Never share it.'
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

from scamguard.llm.otp_guard import otp_signal

SEED = 20261020


def _read_rows(path: Path) -> list[tuple[str, int]]:
    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")
    try:
        contents = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        # Kaggle's common spam.csv is often Windows-1252/Latin-1 encoded.
        contents = path.read_text(encoding="cp1252")
    if path.name.lower() == "smsspamcollection" or path.suffix.lower() in {".tsv", ".txt"}:
        iterator = csv.reader(contents.splitlines(), delimiter="\t")
        entries = [(row[0], row[1]) for row in iterator if len(row) >= 2]
    else:
        iterator = csv.DictReader(contents.splitlines())
        if not iterator.fieldnames:
            raise ValueError("CSV is empty")
        names = {name.lower().strip(): name for name in iterator.fieldnames}
        label_col = names.get("v1") or names.get("label")
        text_col = names.get("v2") or names.get("text")
        if not label_col or not text_col:
            raise ValueError("Expected Kaggle v1,v2 columns or label,text")
        entries = [(row.get(label_col, ""), row.get(text_col, "")) for row in iterator]
    labels = {"ham": 0, "legit": 0, "spam": 1, "scam": 1}
    unique: dict[str, tuple[str, int]] = {}
    for raw_label, raw_text in entries:
        label = labels.get(str(raw_label).strip().lower())
        text = str(raw_text).strip()
        if label is None or not text:
            continue
        # Dedupe before splitting: the same message may not appear in train/test.
        key = re.sub(r"\s+", " ", text.casefold()).strip()
        if key in unique and unique[key][1] != label:
            raise ValueError(f"Conflicting labels for duplicate text: {text[:50]!r}")
        unique[key] = (text, label)
    result = list(unique.values())
    if len(result) < 40 or {label for _, label in result} != {0, 1}:
        raise ValueError("Need at least 40 unique messages and both ham/spam labels")
    return result


def _build_model() -> Pipeline:
    return Pipeline(
        [
            (
                "features",
                FeatureUnion(
                    [
                        (
                            "word",
                            TfidfVectorizer(
                                lowercase=True,
                                ngram_range=(1, 2),
                                min_df=2,
                                sublinear_tf=True,
                                max_features=60000,
                            ),
                        ),
                        (
                            "char",
                            TfidfVectorizer(
                                lowercase=True,
                                analyzer="char_wb",
                                ngram_range=(3, 5),
                                min_df=2,
                                sublinear_tf=True,
                                max_features=90000,
                            ),
                        ),
                    ]
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced", max_iter=2000, random_state=SEED
                ),
            ),
        ]
    )


def _scores(model: Pipeline, texts: list[str]) -> np.ndarray:
    probabilities = model.predict_proba(texts)[:, 1].astype(float)
    # v3 OTP corrections are evaluated, not merely applied after evaluation.
    for index, text in enumerate(texts):
        signal = otp_signal(text)
        if signal == "routine_code":
            probabilities[index] = 0.0
        elif signal == "disclosure_request":
            probabilities[index] = 1.0
    return probabilities


def _choose_threshold(y_val: np.ndarray, scores: np.ndarray, max_fpr: float) -> float:
    """Maximize recall while respecting EMPIRICAL FPR on validation only."""
    negatives = np.sort(scores[y_val == 0])
    if len(negatives) == 0:
        raise ValueError("No legitimate examples for threshold calibration")
    allowed_fps = int(math.floor(max_fpr * len(negatives)))
    if allowed_fps >= len(negatives):
        return 0.0
    # Strictly exceed the next negative to ensure <= allowed_fps even on ties.
    return float(np.nextafter(negatives[-allowed_fps - 1], np.inf))


def _report(y: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, float | int | dict]:
    predicted = (scores >= threshold).astype(int)
    tn, fp, fn, tp = (int(v) for v in confusion_matrix(y, predicted, labels=[0, 1]).ravel())
    benign = tn + fp
    # One-sided exact 95% upper binomial bound if there are zero FPs.
    upper_zero_fp = 1 - 0.05 ** (1 / benign) if fp == 0 and benign else None
    return {
        "threshold": threshold,
        "size": len(y),
        "precision": float(precision_score(y, predicted, zero_division=0)),
        "recall": float(recall_score(y, predicted, zero_division=0)),
        "false_positive_rate": fp / benign if benign else 0.0,
        "zero_fp_upper_95_one_sided": upper_zero_fp,
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }


def train(dataset: Path, output: Path, max_fpr: float) -> dict:
    if not 0 <= max_fpr < 1:
        raise ValueError("max_fpr must be in [0, 1)")
    rows = _read_rows(dataset)
    texts = [text for text, _ in rows]
    labels = np.array([label for _, label in rows], dtype=int)
    # 60% train / 20% validation / 20% test, all disjoint.
    train_and_val, test = train_test_split(
        np.arange(len(texts)), test_size=0.2, stratify=labels, random_state=SEED
    )
    train_idx, val_idx = train_test_split(
        train_and_val,
        test_size=0.25,
        stratify=labels[train_and_val],
        random_state=SEED,
    )
    model = _build_model()
    model.fit([texts[i] for i in train_idx], labels[train_idx])
    val_scores = _scores(model, [texts[i] for i in val_idx])
    threshold = _choose_threshold(labels[val_idx], val_scores, max_fpr)
    test_scores = _scores(model, [texts[i] for i in test])
    result = {
        "source": str(dataset),
        "label_meaning": "spam vs ham (spam is not necessarily a scam)",
        "unique_messages": len(rows),
        "train_size": len(train_idx),
        "validation": _report(labels[val_idx], val_scores, threshold),
        "test": _report(labels[test], test_scores, threshold),
        "notes": (
            "Threshold selected only on validation. Test is held out. "
            "This corpus does not establish performance on modern 2FA or scam-only messages. "
            "No AI-generated training labels are used."
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": model, "threshold": threshold, "training_source": str(dataset)}, output)
    return result


def predict(model_path: Path, text: str) -> dict:
    if not text.strip():
        raise ValueError("Message text cannot be empty")
    # Only load joblib files you produced yourself: pickle formats are executable.
    bundle = joblib.load(model_path)
    score = float(_scores(bundle["pipeline"], [text])[0])
    return {
        "label": "spam" if score >= bundle["threshold"] else "ham",
        "spam_score": score,
        "threshold": bundle["threshold"],
        "otp_signal": otp_signal(text),
        "warning": "Spam score is not a calibrated probability of fraud or proof of sender identity.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    train_parser = commands.add_parser("train", help="fit and held-out evaluation")
    train_parser.add_argument("--input", type=Path, required=True)
    train_parser.add_argument("--output", type=Path, required=True)
    train_parser.add_argument("--max-fpr", type=float, default=0.005)
    predict_parser = commands.add_parser("predict", help="classify a message")
    predict_parser.add_argument("--model", type=Path, required=True)
    predict_parser.add_argument("text")
    args = parser.parse_args()
    if args.command == "train":
        report = train(args.input, args.output, args.max_fpr)
    else:
        report = predict(args.model, args.text)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

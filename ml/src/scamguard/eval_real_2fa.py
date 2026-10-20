"""Audit the v3 LOCAL LLM on independently collected, human-labeled 2FA SMS.

Input CSV: id,text,label   (label: legit or scam)
Messages must be real and verified, not reused from training/prompt examples.
The audit does not retrain or tune thresholds on the audit set.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from scamguard.llm.detector import LocalLLMDetector
from scamguard.llm.ollama import OllamaBackend
from scamguard.taxonomy import DangerLevel


def audit(dataset: Path, model: str, pool: Path, cache: Path) -> dict:
    with dataset.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"text", "label"}.issubset(reader.fieldnames):
            raise ValueError("Expected a CSV containing text,label columns")
        rows = list(reader)
    if not rows:
        raise ValueError("Audit dataset is empty")
    detector = LocalLLMDetector(
        OllamaBackend(model), cache, prompt_version="v3", pool_path=pool
    )
    tn = fp = fn = tp = errors = suspicious_legit = 0
    for row in rows:
        label = row["label"].strip().lower()
        if label not in {"scam", "legit"}:
            raise ValueError("Label must be 'scam' or 'legit' (verified by a human)")
        result = detector.detect(row["text"])
        if not result.ok or result.value is None:
            errors += 1
            continue
        predicted_scam = result.value.danger_level == DangerLevel.DANGEROUS
        if label == "legit":
            if result.value.danger_level == DangerLevel.SUSPICIOUS:
                suspicious_legit += 1
            if predicted_scam:
                fp += 1
            else:
                tn += 1
        elif predicted_scam:
            tp += 1
        else:
            fn += 1
    negatives = tn + fp
    positives = tp + fn
    return {
        "samples": len(rows),
        "evaluated": negatives + positives,
        "errors_not_counted_as_safe": errors,
        "false_positive_rate": fp / negatives if negatives else None,
        "scam_recall": tp / positives if positives else None,
        "legitimate_messages_marked_suspicious": suspicious_legit,
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "model": model,
        "prompt_version": "v3",
        "caveat": "Dangerous is positive; suspicious requires separate review.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--pool", type=Path, default=Path("data/pool/pool.csv"))
    parser.add_argument("--cache", type=Path, default=Path("data/cache/llm.sqlite3"))
    args = parser.parse_args()
    print(json.dumps(audit(args.input, args.model, args.pool, args.cache), indent=2))


if __name__ == "__main__":
    main()

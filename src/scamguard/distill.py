"""Teacher labeling, compact student training, and portable export."""

import argparse
import csv
import json
import time
from collections.abc import Sequence
from pathlib import Path
from statistics import fmean
from typing import Any

import joblib
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from scamguard.eval.metrics import binary_metrics, metric_confidence_intervals
from scamguard.eval.report import load_evaluation_rows
from scamguard.leakage import find_leaks, load_rows
from scamguard.llm.backend import LLMRequest
from scamguard.llm.cache import ResponseCache
from scamguard.llm.detector import LocalLLMDetector
from scamguard.llm.ollama import OllamaBackend
from scamguard.llm.runner import StructuredRunner
from scamguard.taxonomy import DangerLevel

SEED = 20261017
TEACHER_MODEL = "qwen3:4b-instruct-2507-q4_K_M"
TEACHER_PROMPT = "v2"
TEACHER_FEW_SHOTS = 6
PUBLIC_SAMPLE_PER_CLASS = 84
CONFIDENCE = 0.80


class TeacherItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    danger_level: DangerLevel
    score: float = Field(ge=0, le=1)


class TeacherBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[TeacherItem] = Field(min_length=1, max_length=6)

    @model_validator(mode="after")
    def unique_ids(self) -> "TeacherBatch":
        identifiers = [item.id for item in self.items]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("teacher batch returned duplicate ids")
        return self


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_candidates(
    pool_path: Path = Path("data/pool/pool.csv"),
    public_path: Path = Path("data/processed/uci_sms.csv"),
    eval_path: Path = Path("data/eval/test_set.csv"),
) -> list[dict[str, str]]:
    """Combine all pool rows with a deterministic balanced public-data sample."""

    pool = _read_csv(pool_path)
    public = _read_csv(public_path)
    rng = np.random.default_rng(SEED)
    sampled: list[dict[str, str]] = []
    for label in ("legit", "scam"):
        rows = [row for row in public if row["label"] == label]
        indices = rng.choice(len(rows), size=PUBLIC_SAMPLE_PER_CLASS, replace=False)
        sampled.extend(rows[int(index)] for index in indices)
    candidates = [*pool, *sampled]
    leaks = find_leaks(candidates, load_rows(eval_path))
    blocked = {leak.pool_id for leak in leaks}
    return [row for row in candidates if row["id"] not in blocked]


def _batches(
    values: Sequence[dict[str, str]], size: int
) -> list[Sequence[dict[str, str]]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def label_candidates(
    candidates: list[dict[str, str]],
    output_path: Path,
    batch_size: int = 6,
) -> None:
    """Label candidates with the frozen local teacher and append resumable JSONL."""

    prompt_detector = LocalLLMDetector(
        OllamaBackend(TEACHER_MODEL),
        Path("data/cache/distill-prompt.sqlite3"),
        prompt_version=TEACHER_PROMPT,
        few_shot_count=TEACHER_FEW_SHOTS,
    )
    backend = OllamaBackend(TEACHER_MODEL)
    runner = StructuredRunner(
        backend,
        TeacherBatch,
        ResponseCache(Path("data/cache/distill.sqlite3")),
    )
    existing: set[str] = set()
    if output_path.exists():
        existing = {
            str(json.loads(line)["id"])
            for line in output_path.read_text(encoding="utf-8").splitlines()
        }
    remaining = [row for row in candidates if row["id"] not in existing]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    for batch_number, batch in enumerate(_batches(remaining, batch_size), start=1):
        messages = "\n".join(
            f"<MESSAGE id={json.dumps(row['id'])}>{row['text']}</MESSAGE>"
            for row in batch
        )
        request = LLMRequest(
            system_prompt=prompt_detector.prompt.system_prompt,
            user_prompt=(
                "Classify every message independently. Preserve each id exactly and "
                "return one item per message in the same order.\n" + messages
            ),
            json_schema=TeacherBatch.model_json_schema(),
            prompt_version=(
                f"distill-v1:{prompt_detector.prompt.sha256}:batch-{batch_size}"
            ),
            normalized_text="\n".join(f"{row['id']}:{row['text']}" for row in batch),
        )
        result = runner.run(request)
        if result.value is None:
            raise RuntimeError(result.error)
        expected_ids = [row["id"] for row in batch]
        actual_ids = [item.id for item in result.value.items]
        if actual_ids != expected_ids:
            raise RuntimeError(
                f"teacher ids/order mismatch: expected {expected_ids}, got {actual_ids}"
            )
        by_id = {row["id"]: row for row in batch}
        with output_path.open("a", encoding="utf-8") as handle:
            for item in result.value.items:
                source = by_id[item.id]
                record = {
                    "id": item.id,
                    "text": source["text"],
                    "source": source.get("source", "unknown"),
                    "original_label": source["label"],
                    "teacher_score": item.score,
                    "teacher_label": "scam" if item.score >= 0.5 else "legit",
                }
                handle.write(json.dumps(record, separators=(",", ":")) + "\n")
        print(
            f"[teacher] batch {batch_number}/{len(_batches(remaining, batch_size))} "
            f"({len(existing) + min(batch_number * batch_size, len(remaining))}/"
            f"{len(candidates)})"
        )


def _student_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=30_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1_000,
                    random_state=SEED,
                ),
            ),
        ]
    )


def _choose_thresholds(labels: list[int], scores: list[float]) -> tuple[float, float]:
    candidates = sorted({0.0, 1.0, *scores})
    dangerous = max(
        (
            threshold
            for threshold in candidates
            if binary_metrics(labels, scores, threshold)["false_positive_rate"] <= 0.03
        ),
        key=lambda threshold: (
            binary_metrics(labels, scores, threshold)["recall"],
            binary_metrics(labels, scores, threshold)["f1"],
            threshold,
        ),
    )
    safe_candidates = [
        threshold
        for threshold in candidates
        if threshold < dangerous
        and binary_metrics(labels, scores, threshold)["false_negative_rate"] <= 0.05
    ]
    safe = max(safe_candidates, default=0.0)
    return safe, dangerous


def _predict_scores(model: Pipeline, texts: Sequence[str]) -> list[float]:
    probabilities = model.predict_proba(texts)
    return [float(score) for score in probabilities[:, 1]]


def _export_onnx(model: Pipeline, path: Path) -> None:
    from skl2onnx import to_onnx

    exported = to_onnx(model, np.asarray(["sample"], dtype=object), target_opset=17)
    path.write_bytes(exported.SerializeToString())


def _smoke_onnx(path: Path) -> list[float]:
    import onnxruntime as ort

    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: np.asarray(["hello"], dtype=object)})
    probabilities = outputs[-1]
    if isinstance(probabilities, list):
        return [float(value) for value in probabilities[0].values()]
    array = np.asarray(probabilities)
    return [float(value) for value in array.reshape(-1)]


def _try_coreml(model: Pipeline, path: Path) -> str | None:
    try:
        import coremltools as ct

        converted = ct.converters.sklearn.convert(
            model,
            input_features=["text"],
            output_feature_names="scam_probability",
        )
        converted.save(str(path))
    except Exception as error:  # conversion support varies by coremltools release
        return f"{type(error).__name__}: {error}"
    return None


def _export_preprocessing(model: Pipeline, path: Path) -> dict[str, Any]:
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    manifest = {
        "kind": "word_tfidf_1_2_grams",
        "lowercase": True,
        "sublinear_tf": True,
        "vocabulary": {
            token: int(index) for token, index in vectorizer.vocabulary_.items()
        },
        "idf": [float(value) for value in vectorizer.idf_],
        "coefficient": [float(value) for value in classifier.coef_[0]],
        "intercept": float(classifier.intercept_[0]),
    }
    path.write_text(json.dumps(manifest, separators=(",", ":")), encoding="utf-8")
    return manifest


def _export_coreml_head(manifest: dict[str, Any], path: Path) -> str | None:
    """Export the linear head; text TF-IDF remains app-side."""

    try:
        import coremltools as ct
        from coremltools.models import datatypes
        from coremltools.models.neural_network import NeuralNetworkBuilder

        coefficients = np.asarray(manifest["coefficient"], dtype=np.float32)
        feature_count = len(coefficients)
        builder = NeuralNetworkBuilder(
            [("tfidf", datatypes.Array(feature_count))],
            [("scam_probability", datatypes.Array(1))],
        )
        builder.add_inner_product(
            name="logistic_linear",
            W=coefficients.reshape(1, -1),
            b=np.asarray([manifest["intercept"]], dtype=np.float32),
            input_channels=feature_count,
            output_channels=1,
            has_bias=True,
            input_name="tfidf",
            output_name="logit",
        )
        builder.add_activation(
            name="probability",
            non_linearity="SIGMOID",
            input_name="logit",
            output_name="scam_probability",
        )
        ct.models.MLModel(builder.spec).save(str(path))
    except Exception as error:
        return f"{type(error).__name__}: {error}"
    return None


def _smoke_coreml(path: Path, feature_count: int) -> tuple[float | None, str | None]:
    try:
        import coremltools as ct

        model = ct.models.MLModel(str(path))
        result = model.predict(
            {"tfidf": np.zeros(feature_count, dtype=np.float64)}
        )
        probability = float(np.asarray(result["scam_probability"]).reshape(-1)[0])
    except Exception as error:
        return None, f"{type(error).__name__}: {error}"
    return probability, None


def train_student(
    labels_path: Path,
    output_directory: Path,
) -> dict[str, Any]:
    records = [
        json.loads(line)
        for line in labels_path.read_text(encoding="utf-8").splitlines()
    ]
    confident = [
        record
        for record in records
        if record["teacher_score"] >= CONFIDENCE
        or record["teacher_score"] <= 1 - CONFIDENCE
    ]
    texts = [str(record["text"]) for record in confident]
    labels = [int(record["teacher_label"] == "scam") for record in confident]
    train_texts, calibration_texts, train_labels, calibration_labels = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=SEED,
        stratify=labels,
    )
    model = _student_pipeline()
    model.fit(train_texts, train_labels)
    calibration_scores = _predict_scores(model, calibration_texts)
    safe_threshold, dangerous_threshold = _choose_thresholds(
        calibration_labels, calibration_scores
    )

    dev_rows = load_evaluation_rows(Path("data/eval/dev.csv"))
    dev_labels = [int(row["label"] == "scam") for row in dev_rows]
    started = time.perf_counter()
    dev_scores = _predict_scores(model, [row["text"] for row in dev_rows])
    elapsed = time.perf_counter() - started
    dev_metrics = binary_metrics(dev_labels, dev_scores, dangerous_threshold)
    resolved = [
        score <= safe_threshold or score >= dangerous_threshold for score in dev_scores
    ]
    resolved_indices = [index for index, value in enumerate(resolved) if value]
    resolved_correct = sum(
        (dev_scores[index] >= dangerous_threshold) == bool(dev_labels[index])
        for index in resolved_indices
    )

    dev_report = json.loads(
        Path("docs/phase1/results/dev_results.json").read_text(encoding="utf-8")
    )
    teacher_result = next(
        result
        for result in dev_report["results"]
        if result["model"] == TEACHER_MODEL
        and result["prompt_version"] == TEACHER_PROMPT
    )
    teacher_by_id = {
        item["id"]: int(item["predicted"] == "scam")
        for item in teacher_result["predictions"]
    }
    student_binary = [int(score >= dangerous_threshold) for score in dev_scores]
    agreement = sum(
        prediction == teacher_by_id[row["id"]]
        for row, prediction in zip(dev_rows, student_binary, strict=True)
    ) / len(dev_rows)

    output_directory.mkdir(parents=True, exist_ok=True)
    joblib_path = output_directory / "student.joblib"
    onnx_path = output_directory / "student.onnx"
    preprocessing_path = output_directory / "preprocessing.json"
    coreml_path = output_directory / "student-full.mlpackage"
    coreml_head_path = output_directory / "student-linear.mlmodel"
    joblib.dump(model, joblib_path)
    _export_onnx(model, onnx_path)
    smoke_probabilities = _smoke_onnx(onnx_path)
    preprocessing = _export_preprocessing(model, preprocessing_path)
    coreml_error = _try_coreml(model, coreml_path)
    coreml_head_error = _export_coreml_head(preprocessing, coreml_head_path)
    if coreml_head_error is None:
        coreml_probability, coreml_smoke_error = _smoke_coreml(
            coreml_head_path, len(preprocessing["vocabulary"])
        )
    else:
        coreml_probability, coreml_smoke_error = None, coreml_head_error
    summary: dict[str, Any] = {
        "teacher": {
            "model": TEACHER_MODEL,
            "prompt": TEACHER_PROMPT,
            "candidate_count": len(records),
            "confident_kept": len(confident),
            "uncertain_dropped": len(records) - len(confident),
            "confidence_cutoffs": [1 - CONFIDENCE, CONFIDENCE],
            "agreement_with_original_labels": fmean(
                record["teacher_label"] == record["original_label"]
                for record in records
            ),
        },
        "student": {
            "type": "word TF-IDF (1-2 grams) plus logistic regression",
            "training_examples": len(train_texts),
            "calibration_examples": len(calibration_texts),
            "safe_threshold": safe_threshold,
            "dangerous_threshold": dangerous_threshold,
            "dev_metrics": dev_metrics,
            "dev_confidence_intervals_95": metric_confidence_intervals(dev_metrics),
            "teacher_agreement_on_dev": agreement,
            "dev_latency_ms_per_message": elapsed / len(dev_rows) * 1_000,
            "dev_resolved_fraction": len(resolved_indices) / len(dev_rows),
            "dev_resolved_accuracy": resolved_correct / len(resolved_indices)
            if resolved_indices
            else 0.0,
        },
        "exports": {
            "joblib_bytes": joblib_path.stat().st_size,
            "onnx_bytes": onnx_path.stat().st_size,
            "preprocessing_bytes": preprocessing_path.stat().st_size,
            "feature_count": len(preprocessing["vocabulary"]),
            "onnx_smoke_probabilities": smoke_probabilities,
            "quantization": "none (float32; compact sparse linear model)",
            "coreml_path": str(coreml_path) if coreml_error is None else None,
            "coreml_error": coreml_error,
            "coreml_linear_head_path": str(coreml_head_path)
            if coreml_head_error is None
            else None,
            "coreml_linear_head_bytes": coreml_head_path.stat().st_size
            if coreml_head_error is None
            else None,
            "coreml_linear_head_error": coreml_head_error,
            "coreml_smoke_probability": coreml_probability,
            "coreml_smoke_error": coreml_smoke_error,
            "onnx_path": str(onnx_path),
        },
        "test_evaluation": (
            "not rerun: the single frozen TEST evaluation was already completed in "
            "Step 6; preserving the lock takes precedence"
        ),
    }
    (output_directory / "metrics.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Distill the local teacher")
    parser.add_argument("command", choices=("label", "train", "all"))
    parser.add_argument(
        "--labels", type=Path, default=Path("data/distill/teacher_labels.jsonl")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/student")
    )
    return parser.parse_args()


def main() -> None:
    args = _arguments()
    if args.command in {"label", "all"}:
        candidates = build_candidates()
        print(f"Prepared {len(candidates)} non-eval candidates")
        label_candidates(candidates, args.labels)
    if args.command in {"train", "all"}:
        summary = train_student(args.labels, args.output)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

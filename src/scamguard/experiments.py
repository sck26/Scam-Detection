"""Run reproducible local-LLM experiments on the development set only."""

import argparse
import json
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean, median
from typing import Any, cast

import numpy as np
from sklearn.linear_model import LogisticRegression

from scamguard.eval.access import DEFAULT_DEV_PATH
from scamguard.eval.metrics import (
    binary_metrics,
    metric_confidence_intervals,
    tactic_metrics,
    threshold_sweep,
)
from scamguard.eval.report import load_evaluation_rows
from scamguard.llm.detector import LocalLLMDetector
from scamguard.llm.ollama import OllamaBackend
from scamguard.model_setup import load_manifest


def _percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        return 0.0
    return float(np.percentile(np.asarray(values), percentile))


def _fit_platt(
    labels: list[int], scores: list[float]
) -> tuple[list[float], dict[str, float]]:
    features = np.asarray(scores, dtype=float).reshape(-1, 1)
    classifier = LogisticRegression(random_state=0)
    classifier.fit(features, labels)
    calibrated = classifier.predict_proba(features)[:, 1]
    coefficients = cast(np.ndarray[Any, np.dtype[np.float64]], classifier.coef_)
    intercepts = cast(np.ndarray[Any, np.dtype[np.float64]], classifier.intercept_)
    return [float(value) for value in calibrated], {
        "coefficient": float(coefficients[0, 0]),
        "intercept": float(intercepts[0]),
    }


def _reliability(
    labels: Sequence[int], scores: Sequence[float]
) -> list[dict[str, Any]]:
    bins: list[dict[str, Any]] = []
    for lower_value in np.linspace(0.0, 0.8, 5):
        lower = float(lower_value)
        upper = lower + 0.2
        indices = [
            index
            for index, score in enumerate(scores)
            if lower <= score < upper or (upper >= 1.0 and score == 1.0)
        ]
        bins.append(
            {
                "range": [lower, min(upper, 1.0)],
                "count": len(indices),
                "mean_score": fmean(scores[index] for index in indices)
                if indices
                else None,
                "observed_scam_rate": fmean(labels[index] for index in indices)
                if indices
                else None,
            }
        )
    return bins


def _breakdowns(
    rows: Sequence[dict[str, str]],
    scores: Sequence[float],
    threshold: float,
    field: str,
) -> dict[str, dict[str, Any]]:
    groups: defaultdict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[row[field]].append(index)
    return {
        group: {
            **binary_metrics(
                [int(rows[index]["label"] == "scam") for index in indices],
                [scores[index] for index in indices],
                threshold,
            ),
            "count": len(indices),
        }
        for group, indices in sorted(groups.items())
    }


def _checkpoint_path(directory: Path, model: str, prompt: str) -> Path:
    safe_model = model.replace(":", "_").replace("/", "_")
    return directory / f"{safe_model}-{prompt}.jsonl"


def _load_checkpoint(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    records: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        records[str(record["id"])] = record
    return records


def _append_checkpoint(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def run_combination(
    model: str,
    prompt_version: str,
    few_shot_count: int,
    rows: list[dict[str, str]],
    checkpoint_directory: Path,
    cache_path: Path,
    max_fpr: float,
) -> dict[str, Any]:
    """Run and summarize one model/prompt combination."""

    detector = LocalLLMDetector(
        OllamaBackend(model),
        cache_path,
        prompt_version=prompt_version,
        few_shot_count=few_shot_count,
    )
    checkpoint = _checkpoint_path(checkpoint_directory, model, prompt_version)
    records = _load_checkpoint(checkpoint)
    for index, row in enumerate(rows, start=1):
        if row["id"] in records:
            continue
        result = detector.detect(row["text"])
        record: dict[str, Any] = {
            "id": row["id"],
            "actual": row["label"],
            "expected_tactics": list(filter(None, row["tactics"].split("|"))),
            "attempts": result.attempts,
            "error": result.error,
            "latency_seconds": result.response.latency_seconds,
            "input_tokens": result.response.input_tokens,
            "output_tokens": result.response.output_tokens,
            "tokens_per_second": result.response.tokens_per_second,
            "cached": result.response.cached,
            "output": result.value.model_dump(mode="json") if result.value else None,
        }
        _append_checkpoint(checkpoint, record)
        records[row["id"]] = record
        print(f"[{model} {prompt_version}] {index}/{len(rows)} {row['id']}")

    ordered = [records[row["id"]] for row in rows]
    valid_pairs = [
        (row, record)
        for row, record in zip(rows, ordered, strict=True)
        if record["output"]
    ]
    if not valid_pairs:
        raise RuntimeError(f"no valid responses for {model} {prompt_version}")
    valid_rows = [row for row, _ in valid_pairs]
    valid_records = [record for _, record in valid_pairs]
    labels = [int(row["label"] == "scam") for row in valid_rows]
    raw_scores = [float(record["output"]["score"]) for record in valid_records]
    calibrated_scores, platt = _fit_platt(labels, raw_scores)
    sweep = threshold_sweep(labels, calibrated_scores, max_fpr)
    dangerous_threshold = float(sweep["recommended"]["threshold"])
    eligible_suspicious = [
        point
        for point in sweep["points"]
        if float(point["threshold"]) < dangerous_threshold
    ]
    suspicious_threshold = (
        float(
            max(eligible_suspicious, key=lambda point: float(point["f1"]))[
                "threshold"
            ]
        )
        if eligible_suspicious
        else max(0.0, dangerous_threshold / 2)
    )
    metrics = binary_metrics(labels, calibrated_scores, dangerous_threshold)
    latencies = [
        float(record["latency_seconds"])
        for record in valid_records
        if not record["cached"]
    ]
    throughputs = [
        float(record["tokens_per_second"])
        for record in valid_records
        if record["tokens_per_second"] is not None and not record["cached"]
    ]
    expected_tactics = [set(record["expected_tactics"]) for record in valid_records]
    predicted_tactics = [set(record["output"]["tactics"]) for record in valid_records]
    predictions = []
    for row, record, score in zip(
        valid_rows, valid_records, calibrated_scores, strict=True
    ):
        predictions.append(
            {
                "id": row["id"],
                "actual": row["label"],
                "raw_score": float(record["output"]["score"]),
                "calibrated_score": score,
                "predicted": "scam" if score >= dangerous_threshold else "legit",
                "output": record["output"],
            }
        )
    return {
        "model": model,
        "prompt_version": detector.prompt.version,
        "prompt_sha256": detector.prompt.sha256,
        "few_shot_count": len(detector.prompt.few_shot_ids),
        "few_shot_ids": list(detector.prompt.few_shot_ids),
        "examples": len(rows),
        "valid_responses": len(valid_records),
        "errors": len(rows) - len(valid_records),
        "calibration": {
            "method": "Platt scaling (fit on DEV)",
            **platt,
            "reliability": _reliability(labels, calibrated_scores),
        },
        "thresholds": {
            "safe_below": suspicious_threshold,
            "suspicious_below": dangerous_threshold,
            "dangerous_at_or_above": dangerous_threshold,
        },
        "metrics": metrics,
        "confidence_intervals_95": metric_confidence_intervals(metrics),
        "threshold_sweep": sweep,
        "per_category": _breakdowns(
            valid_rows, calibrated_scores, dangerous_threshold, "scam_category"
        ),
        "per_channel": _breakdowns(
            valid_rows, calibrated_scores, dangerous_threshold, "channel"
        ),
        "tactic_metrics": tactic_metrics(expected_tactics, predicted_tactics),
        "performance": {
            "measured_uncached_responses": len(latencies),
            "median_latency_seconds": median(latencies) if latencies else None,
            "p95_latency_seconds": _percentile(latencies, 95) if latencies else None,
            "mean_tokens_per_second": fmean(throughputs) if throughputs else None,
        },
        "predictions": predictions,
        "error_records": [record for record in ordered if record["error"]],
    }


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local-LLM DEV experiments")
    parser.add_argument("--data", type=Path, default=DEFAULT_DEV_PATH)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("reports/runs"))
    parser.add_argument("--cache", type=Path, default=Path("data/cache/llm.sqlite3"))
    parser.add_argument("--max-fpr", type=float, default=0.05)
    parser.add_argument("--models", nargs="*")
    return parser.parse_args()


def main() -> None:
    args = _arguments()
    if args.data.resolve() != DEFAULT_DEV_PATH.resolve():
        raise SystemExit("experiments are DEV-only; final TEST uses the frozen runner")
    rows = load_evaluation_rows(args.data)
    models = args.models or [model.tag for model in load_manifest().models]
    combinations = [("v1", 0), ("v2", 6)]
    results = [
        run_combination(
            model,
            prompt,
            count,
            rows,
            args.checkpoint_dir,
            args.cache,
            args.max_fpr,
        )
        for model in models
        for prompt, count in combinations
    ]
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "data": str(args.data),
        "max_fpr": args.max_fpr,
        "calibration_note": (
            "Platt scaling and thresholds are fit on DEV and are not unbiased "
            "generalization estimates. TEST remains locked."
        ),
        "results": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

"""One-shot evaluation of the frozen detector and baselines on locked TEST."""

import argparse
import json
import math
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from statistics import fmean, median
from typing import Any

import numpy as np
import yaml
from pydantic import BaseModel, ConfigDict, Field

from scamguard.eval.access import (
    LOCKED_TEST_PATH,
    guard_evaluation_access,
    record_test_completion,
)
from scamguard.eval.detectors import (
    AlwaysScamDetector,
    Prediction,
    RandomDetector,
    TfidfLogisticDetector,
)
from scamguard.eval.metrics import (
    binary_metrics,
    metric_confidence_intervals,
    tactic_metrics,
)
from scamguard.eval.report import evaluate_detector, load_evaluation_rows
from scamguard.llm.detector import LocalLLMDetector
from scamguard.llm.ollama import OllamaBackend
from scamguard.taxonomy import DangerLevel, TacticName


class FrozenConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    model: str
    prompt_version: str
    prompt_sha256: str = Field(min_length=64, max_length=64)
    few_shot_count: int = Field(ge=0)
    few_shot_ids: tuple[str, ...]
    platt_coefficient: float
    platt_intercept: float
    safe_below: float = Field(ge=0, le=1)
    dangerous_at_or_above: float = Field(ge=0, le=1)


def load_frozen_config() -> FrozenConfig:
    path = files("scamguard").joinpath("frozen.yaml")
    return FrozenConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def calibrate(raw_score: float, config: FrozenConfig) -> float:
    """Apply the Platt transform frozen from DEV."""

    logit = config.platt_coefficient * raw_score + config.platt_intercept
    return 1.0 / (1.0 + math.exp(-logit))


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


def _summarize_frozen(
    rows: list[dict[str, str]],
    predictions: list[Prediction],
    raw_records: list[dict[str, Any]],
    config: FrozenConfig,
) -> dict[str, Any]:
    expected = [int(row["label"] == "scam") for row in rows]
    scores = [prediction.score for prediction in predictions]
    metrics = binary_metrics(expected, scores, config.dangerous_at_or_above)
    expected_tactics = [set(filter(None, row["tactics"].split("|"))) for row in rows]
    predicted_tactics = [
        {tactic.value for tactic in prediction.tactics} for prediction in predictions
    ]
    latencies = [float(record["latency_seconds"]) for record in raw_records]
    throughputs = [
        float(record["tokens_per_second"])
        for record in raw_records
        if record["tokens_per_second"] is not None
    ]
    predicted_binary = [score >= config.dangerous_at_or_above for score in scores]
    return {
        "name": "frozen_local_llm",
        "model": config.model,
        "prompt_version": config.prompt_version,
        "prompt_sha256": config.prompt_sha256,
        "few_shot_ids": list(config.few_shot_ids),
        "thresholds": {
            "safe_below": config.safe_below,
            "dangerous_at_or_above": config.dangerous_at_or_above,
        },
        "calibration": {
            "method": "Platt scaling frozen on DEV",
            "coefficient": config.platt_coefficient,
            "intercept": config.platt_intercept,
        },
        "metrics": metrics,
        "confidence_intervals_95": metric_confidence_intervals(metrics),
        "errors": sum(record["error"] is not None for record in raw_records),
        "error_metric_policy": "explicit errors are conservatively scored positive",
        "per_category": _breakdowns(
            rows, scores, config.dangerous_at_or_above, "scam_category"
        ),
        "per_channel": _breakdowns(
            rows, scores, config.dangerous_at_or_above, "channel"
        ),
        "tactic_metrics": tactic_metrics(expected_tactics, predicted_tactics),
        "performance": {
            "median_latency_seconds": median(latencies),
            "p95_latency_seconds": float(np.percentile(latencies, 95)),
            "mean_tokens_per_second": fmean(throughputs),
        },
        "misclassified": [
            {
                "id": row["id"],
                "actual": row["label"],
                "predicted": "scam" if predicted_binary[index] else "legit",
                "calibrated_score": scores[index],
                "raw_score": raw_records[index]["raw_score"],
            }
            for index, row in enumerate(rows)
            if expected[index] != int(predicted_binary[index])
        ],
        "predictions": raw_records,
    }


def _run_frozen(
    rows: list[dict[str, str]], config: FrozenConfig
) -> tuple[list[Prediction], list[dict[str, Any]]]:
    detector = LocalLLMDetector(
        OllamaBackend(config.model),
        Path("data/cache/final.sqlite3"),
        prompt_version=config.prompt_version,
        few_shot_count=config.few_shot_count,
    )
    if detector.prompt.sha256 != config.prompt_sha256:
        raise RuntimeError("frozen prompt hash mismatch; refusing TEST evaluation")
    if detector.prompt.few_shot_ids != config.few_shot_ids:
        raise RuntimeError(
            "frozen few-shot selection mismatch; refusing TEST evaluation"
        )

    predictions: list[Prediction] = []
    records: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        result = detector.detect(row["text"])
        if result.value is None:
            score = 1.0
            tactics: tuple[TacticName, ...] = ()
            output: dict[str, Any] | None = None
        else:
            score = calibrate(result.value.score, config)
            tactics = tuple(result.value.tactics)
            output = result.value.model_dump(mode="json")
        predictions.append(
            Prediction(
                score=score,
                danger_level=DangerLevel.DANGEROUS,
                tactics=tactics,
            )
        )
        records.append(
            {
                "id": row["id"],
                "actual": row["label"],
                "raw_score": result.value.score if result.value else None,
                "calibrated_score": score,
                "output": output,
                "error": result.error,
                "attempts": result.attempts,
                "latency_seconds": result.response.latency_seconds,
                "tokens_per_second": result.response.tokens_per_second,
            }
        )
        print(f"[FINAL {config.model}] {index}/{len(rows)} {row['id']}")
    return predictions, records


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the frozen TEST evaluation once")
    parser.add_argument("--final", action="store_true", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--train-data", type=Path, default=Path("data/processed"))
    return parser.parse_args()


def main() -> None:
    args = _arguments()
    config = load_frozen_config()
    data_path = guard_evaluation_access(LOCKED_TEST_PATH, args.final)
    rows = load_evaluation_rows(data_path)
    predictions, records = _run_frozen(rows, config)
    llm_result = _summarize_frozen(rows, predictions, records, config)
    baselines = [
        AlwaysScamDetector(),
        RandomDetector(),
        TfidfLogisticDetector(args.train_data),
    ]
    baseline_results = []
    for detector in baselines:
        result = evaluate_detector(detector, rows, 0.05)
        result["confidence_intervals_95"] = metric_confidence_intervals(
            result["metrics"]
        )
        baseline_results.append(result)
    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "data": str(data_path),
        "examples": len(rows),
        "selection_frozen_from": "docs/phase1/results/dev_results.json",
        "models": [llm_result, *baseline_results],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    record_test_completion(data_path)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()

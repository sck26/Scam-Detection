"""Evaluation execution and report rendering."""

import csv
import json
import shutil
from collections import defaultdict
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scamguard.eval.detectors import Detector
from scamguard.eval.metrics import binary_metrics, tactic_metrics, threshold_sweep


def load_evaluation_rows(path: Path) -> list[dict[str, str]]:
    """Load the validated evaluation CSV."""

    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _breakdowns(
    rows: Sequence[dict[str, str]], scores: Sequence[float], field: str
) -> dict[str, dict[str, Any]]:
    groups: defaultdict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[row[field]].append(index)
    result: dict[str, dict[str, Any]] = {}
    for group, indices in sorted(groups.items()):
        expected = [int(rows[index]["label"] == "scam") for index in indices]
        group_scores = [scores[index] for index in indices]
        result[group] = binary_metrics(expected, group_scores)
        result[group]["count"] = len(indices)
    return result


def evaluate_detector(
    detector: Detector,
    rows: Sequence[dict[str, str]],
    max_fpr: float,
) -> dict[str, Any]:
    """Evaluate one detector and return JSON-serializable results."""

    predictions = detector.predict([row["text"] for row in rows])
    if len(predictions) != len(rows):
        message = "detector returned a different number of predictions than inputs"
        raise ValueError(message)
    expected = [int(row["label"] == "scam") for row in rows]
    scores = [prediction.score for prediction in predictions]
    metrics = binary_metrics(expected, scores)
    predicted_labels = [int(score >= 0.5) for score in scores]
    misclassified = [
        {
            "id": row["id"],
            "text": row["text"],
            "actual": row["label"],
            "predicted": "scam" if predicted_labels[index] else "legit",
            "score": scores[index],
        }
        for index, row in enumerate(rows)
        if expected[index] != predicted_labels[index]
    ]
    expected_tactics = [set(filter(None, row["tactics"].split("|"))) for row in rows]
    predicted_tactics = [
        {tactic.value for tactic in prediction.tactics} for prediction in predictions
    ]
    emits_tactics = any(predicted_tactics)
    return {
        "name": detector.name,
        "metrics": metrics,
        "threshold_sweep": threshold_sweep(expected, scores, max_fpr),
        "per_category": _breakdowns(rows, scores, "scam_category"),
        "per_channel": _breakdowns(rows, scores, "channel"),
        "tactic_metrics": tactic_metrics(expected_tactics, predicted_tactics)
        if emits_tactics
        else None,
        "misclassified": misclassified,
    }


def _percentage(value: float) -> str:
    return f"{value:.1%}"


def render_markdown(report: dict[str, Any]) -> str:
    """Render the key results and errors for human review."""

    lines = [
        "# ScamGuard baseline evaluation",
        "",
        f"Generated: {report['generated_at']}",
        f"Evaluation data: `{report['data']}` ({report['examples']} examples)",
        f"Maximum false-positive rate for threshold selection: {report['max_fpr']:.1%}",
        "",
        "## Summary",
        "",
        "| Model | Precision | Recall | F1 | FPR | FNR | Accuracy |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for model in report["models"]:
        metrics = model["metrics"]
        lines.append(
            f"| {model['name']} | {_percentage(metrics['precision'])} | "
            f"{_percentage(metrics['recall'])} | {_percentage(metrics['f1'])} | "
            f"{_percentage(metrics['false_positive_rate'])} | "
            f"{_percentage(metrics['false_negative_rate'])} | "
            f"{_percentage(metrics['accuracy'])} |"
        )
    for model in report["models"]:
        metrics = model["metrics"]
        recommended = model["threshold_sweep"]["recommended"]
        matrix = metrics["confusion_matrix"]
        lines.extend(
            [
                "",
                f"## {model['name']}",
                "",
                f"Confusion matrix: TN={matrix['tn']}, FP={matrix['fp']}, "
                f"FN={matrix['fn']}, TP={matrix['tp']}.",
                f"Recommended threshold at FPR <= {report['max_fpr']:.1%}: "
                f"{recommended['threshold']:.4f} (precision "
                f"{_percentage(recommended['precision'])}, recall "
                f"{_percentage(recommended['recall'])}).",
                "",
                "### Per-channel breakdown",
                "",
                "| Channel | Count | Precision | Recall | FPR |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for channel, values in model["per_channel"].items():
            lines.append(
                f"| {channel} | {values['count']} | "
                f"{_percentage(values['precision'])} | "
                f"{_percentage(values['recall'])} | "
                f"{_percentage(values['false_positive_rate'])} |"
            )
        lines.extend(["", "### Misclassified examples", ""])
        if not model["misclassified"]:
            lines.append("None.")
        else:
            for item in model["misclassified"]:
                safe_text = item["text"].replace("\n", " ")
                lines.append(
                    f"- `{item['id']}` actual={item['actual']}, "
                    f"predicted={item['predicted']}, score={item['score']:.4f}: "
                    f"{safe_text}"
                )
    lines.extend(
        [
            "",
            "Full threshold sweeps, per-category metrics, and tactic metrics are in "
            "the JSON report.",
            "",
        ]
    )
    return "\n".join(lines)


def write_reports(
    models: Sequence[dict[str, Any]],
    data_path: Path,
    output_directory: Path,
    max_fpr: float,
    example_count: int,
) -> tuple[Path, Path]:
    """Write timestamped and latest JSON/Markdown copies."""

    generated = datetime.now(UTC)
    stamp = generated.strftime("%Y%m%dT%H%M%SZ")
    report: dict[str, Any] = {
        "generated_at": generated.isoformat(),
        "data": str(data_path),
        "examples": example_count,
        "max_fpr": max_fpr,
        "models": list(models),
    }
    output_directory.mkdir(parents=True, exist_ok=True)
    json_path = output_directory / f"evaluation-{stamp}.json"
    markdown_path = output_directory / f"evaluation-{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    shutil.copyfile(json_path, output_directory / "latest.json")
    shutil.copyfile(markdown_path, output_directory / "latest.md")
    return json_path, markdown_path

"""Binary and tactic-level evaluation metrics."""

from collections.abc import Sequence
from math import inf, nextafter
from typing import Any

from sklearn.metrics import confusion_matrix, precision_recall_curve

from scamguard.taxonomy import TacticName


def _divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def binary_metrics(
    expected: Sequence[int], scores: Sequence[float], threshold: float = 0.5
) -> dict[str, Any]:
    """Calculate scam-positive classification metrics."""

    predicted = [int(score >= threshold) for score in scores]
    matrix = confusion_matrix(expected, predicted, labels=[0, 1])
    tn, fp, fn, tp = (int(value) for value in matrix.ravel())
    precision = _divide(tp, tp + fp)
    recall = _divide(tp, tp + fn)
    return {
        "threshold": threshold,
        "precision": precision,
        "recall": recall,
        "f1": _divide(2 * precision * recall, precision + recall),
        "false_positive_rate": _divide(fp, fp + tn),
        "false_negative_rate": _divide(fn, fn + tp),
        "accuracy": _divide(tp + tn, tp + tn + fp + fn),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }


def threshold_sweep(
    expected: Sequence[int], scores: Sequence[float], max_fpr: float
) -> dict[str, Any]:
    """Build a precision/recall curve and select a high-recall safe threshold."""

    upper_bound = nextafter(max(scores, default=1.0), inf)
    candidates = sorted({0.0, 1.0, upper_bound, *scores})
    points: list[dict[str, float]] = []
    eligible: list[dict[str, float]] = []
    for threshold in candidates:
        metrics = binary_metrics(expected, scores, threshold)
        point = {
            "threshold": threshold,
            "precision": float(metrics["precision"]),
            "recall": float(metrics["recall"]),
            "f1": float(metrics["f1"]),
            "false_positive_rate": float(metrics["false_positive_rate"]),
        }
        points.append(point)
        if point["false_positive_rate"] <= max_fpr:
            eligible.append(point)
    recommended = max(
        eligible,
        key=lambda point: (point["recall"], point["f1"], point["threshold"]),
    )
    precision, recall, thresholds = precision_recall_curve(expected, scores)
    curve = [
        {
            "precision": float(precision[index]),
            "recall": float(recall[index]),
            "threshold": float(threshold),
        }
        for index, threshold in enumerate(thresholds)
    ]
    return {
        "max_false_positive_rate": max_fpr,
        "recommended": recommended,
        "points": points,
        "precision_recall_curve": curve,
    }


def tactic_metrics(
    expected: Sequence[set[str]], predicted: Sequence[set[str]]
) -> dict[str, dict[str, float | int]]:
    """Calculate independent per-tactic precision and recall."""

    result: dict[str, dict[str, float | int]] = {}
    pairs = list(zip(expected, predicted, strict=True))
    for tactic in TacticName:
        name = tactic.value
        tp = sum(name in truth and name in guess for truth, guess in pairs)
        fp = sum(name not in truth and name in guess for truth, guess in pairs)
        fn = sum(name in truth and name not in guess for truth, guess in pairs)
        result[name] = {
            "precision": _divide(tp, tp + fp),
            "recall": _divide(tp, tp + fn),
            "support": tp + fn,
        }
    return result

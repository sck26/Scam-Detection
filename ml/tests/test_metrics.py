import pytest

from scamguard.eval.metrics import binary_metrics, tactic_metrics, threshold_sweep


def test_binary_metrics_known_confusion_matrix() -> None:
    metrics = binary_metrics([0, 0, 1, 1], [0.1, 0.8, 0.4, 0.9])

    assert metrics["confusion_matrix"] == {"tn": 1, "fp": 1, "fn": 1, "tp": 1}
    for name in (
        "precision",
        "recall",
        "f1",
        "false_positive_rate",
        "false_negative_rate",
        "accuracy",
    ):
        assert metrics[name] == pytest.approx(0.5)


def test_threshold_recommendation_respects_max_fpr() -> None:
    sweep = threshold_sweep([0, 0, 1, 1], [0.1, 0.8, 0.4, 0.9], max_fpr=0.0)

    assert sweep["recommended"]["false_positive_rate"] == 0.0
    assert sweep["recommended"]["threshold"] == pytest.approx(0.9)
    assert sweep["recommended"]["recall"] == pytest.approx(0.5)


def test_threshold_sweep_can_recommend_flagging_nothing() -> None:
    sweep = threshold_sweep([0, 1], [1.0, 1.0], max_fpr=0.05)

    assert sweep["recommended"]["threshold"] > 1.0
    assert sweep["recommended"]["false_positive_rate"] == 0.0
    assert sweep["recommended"]["recall"] == 0.0


def test_tactic_metrics_known_values() -> None:
    metrics = tactic_metrics(
        [{"urgency"}, {"urgency", "threat"}, set()],
        [{"urgency"}, {"threat"}, {"urgency"}],
    )

    assert metrics["urgency"]["precision"] == pytest.approx(0.5)
    assert metrics["urgency"]["recall"] == pytest.approx(0.5)
    assert metrics["threat"]["precision"] == pytest.approx(1.0)
    assert metrics["threat"]["recall"] == pytest.approx(1.0)

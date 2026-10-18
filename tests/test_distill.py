from pathlib import Path

from scamguard.distill import _choose_thresholds, build_candidates


def test_distillation_candidates_exclude_eval_ids_and_are_balanced() -> None:
    processed = Path("data/processed/uci_sms.csv")
    if not processed.exists():
        return
    candidates = build_candidates()
    labels = [row["label"] for row in candidates]

    assert len(candidates) <= 600
    assert labels.count("scam") == labels.count("legit")
    assert all(row["id"].startswith(("pool_", "uci_sms_")) for row in candidates)


def test_student_thresholds_respect_calibration_constraints() -> None:
    labels = [0, 0, 0, 1, 1, 1]
    scores = [0.01, 0.1, 0.2, 0.7, 0.8, 0.9]

    safe, dangerous = _choose_thresholds(labels, scores)

    assert safe < dangerous
    assert dangerous == 0.7

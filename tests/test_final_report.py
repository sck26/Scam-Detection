import json
from pathlib import Path

from scamguard.final_report import render_final_report


def test_final_report_states_target_and_lock() -> None:
    path = Path("docs/phase1/results/final_results.json")
    if not path.exists():
        return
    report = render_final_report(json.loads(path.read_text(encoding="utf-8")))

    assert "single audited TEST run" in report
    assert "primary target" in report
    assert "No thresholds" in report

import json
from pathlib import Path

from scamguard.dev_report import render_dev_report


def test_dev_report_renders_real_result_shape() -> None:
    path = Path("docs/phase1/results/dev_results.json")
    if not path.exists():
        return
    report = json.loads(path.read_text(encoding="utf-8"))

    rendered = render_dev_report(report)

    assert "TEST remained locked" in rendered
    assert "## Written error analysis" in rendered
    assert rendered.count("Prompt SHA-256") == len(report["results"])

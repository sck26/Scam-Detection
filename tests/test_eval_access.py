from pathlib import Path

import pytest

from scamguard.eval.access import guard_evaluation_access, record_test_completion


def test_default_run_cannot_touch_locked_test(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    locked = tmp_path / "data" / "eval" / "test.csv"
    locked.parent.mkdir(parents=True)
    locked.touch()

    with pytest.raises(PermissionError, match="--final"):
        guard_evaluation_access(locked, final=False, log_path=tmp_path / "runs.log")

    assert not (tmp_path / "runs.log").exists()


def test_final_run_is_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    locked = tmp_path / "data" / "eval" / "test.csv"
    locked.parent.mkdir(parents=True)
    locked.touch()
    log = tmp_path / "reports" / "test_runs.log"

    assert guard_evaluation_access(locked, final=True, log_path=log) == locked
    assert "STARTED" in log.read_text(encoding="utf-8")

    record_test_completion(locked, log_path=log)
    contents = log.read_text(encoding="utf-8")
    assert contents.count("STARTED") == 1
    assert contents.count("COMPLETED") == 1

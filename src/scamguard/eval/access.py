"""Access guard for the locked held-out evaluation set."""

import sys
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_DEV_PATH = Path("data/eval/dev.csv")
LOCKED_TEST_PATH = Path("data/eval/test.csv")


def guard_evaluation_access(
    data_path: Path,
    final: bool,
    log_path: Path = Path("reports/test_runs.log"),
) -> Path:
    """Reject accidental test access and audit every explicit final run."""

    normalized = data_path.resolve()
    locked = LOCKED_TEST_PATH.resolve()
    if normalized == locked and not final:
        raise PermissionError("locked TEST requires the explicit --final flag")
    if final and normalized != locked:
        raise ValueError("--final may only be used with data/eval/test.csv")
    if final:
        warning = "WARNING: scoring the locked TEST set; this run is auditable"
        print(warning, file=sys.stderr)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).isoformat()
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{timestamp}\tSTARTED\t{normalized}\n")
    return data_path


def record_test_completion(
    data_path: Path,
    status: str = "COMPLETED",
    log_path: Path = Path("reports/test_runs.log"),
) -> None:
    """Append the terminal status of an already-authorized final run."""

    if data_path.resolve() != LOCKED_TEST_PATH.resolve():
        raise ValueError("completion records are only valid for locked TEST")
    timestamp = datetime.now(UTC).isoformat()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp}\t{status}\t{data_path.resolve()}\n")

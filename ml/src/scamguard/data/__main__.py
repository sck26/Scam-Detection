"""CLI entry point for public dataset preparation."""

from collections.abc import Callable
from pathlib import Path

from scamguard.data.sources import (
    download_openphish,
    download_phishtank,
    download_uci_sms,
    download_urlhaus,
    process_spearphishmx,
)

DataTask = Callable[[Path, Path], int | None]


def main() -> None:
    """Run every approved source task, allowing documented skips."""

    root = Path.cwd()
    raw_dir = root / "data" / "raw"
    processed_dir = root / "data" / "processed"
    tasks: tuple[tuple[str, DataTask], ...] = (
        ("UCI SMS", download_uci_sms),
        ("SpearPhishMX", process_spearphishmx),
        ("URLhaus", download_urlhaus),
        ("OpenPhish", download_openphish),
        ("PhishTank", download_phishtank),
    )
    for name, task in tasks:
        count = task(raw_dir, processed_dir)
        if count is not None:
            print(f"OK {name}: wrote {count} normalized rows")


if __name__ == "__main__":
    main()

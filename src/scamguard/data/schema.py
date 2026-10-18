"""Unified schema helpers for local processed datasets."""

import csv
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from scamguard.taxonomy import Channel

COLUMNS = ("id", "text", "label", "channel", "source", "license", "collected_at")


@dataclass(frozen=True, slots=True)
class DatasetRecord:
    """One normalized training example."""

    id: str
    text: str
    label: Literal["scam", "legit"]
    channel: Channel
    source: str
    license: str
    collected_at: str


def write_records(records: Sequence[DatasetRecord], path: Path) -> None:
    """Write records with a stable column order."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))

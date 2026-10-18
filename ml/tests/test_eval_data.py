import csv
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from scamguard.taxonomy import Channel, ScamCategory, TacticName

EVAL_PATH = Path(__file__).parents[2] / "data" / "eval" / "test_set.csv"
EXPECTED_COLUMNS = (
    "id",
    "text",
    "label",
    "scam_category",
    "channel",
    "tactics",
    "has_url",
    "source",
    "notes",
)
URL_PATTERN = re.compile(r"https?://[^\s]+")
PHONE_PATTERN = re.compile(r"\b\d{3}-\d{4}\b")


def _rows() -> list[dict[str, str]]:
    with EVAL_PATH.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert tuple(reader.fieldnames or ()) == EXPECTED_COLUMNS
        return list(reader)


def test_eval_set_schema_balance_and_uniqueness() -> None:
    rows = _rows()
    counts = Counter(row["label"] for row in rows)

    assert len(rows) >= 150
    assert counts == {"scam": 70, "legit": 80}
    assert len({row["id"] for row in rows}) == len(rows)
    assert len({row["text"].casefold() for row in rows}) == len(rows)
    assert {row["source"] for row in rows} == {"synthetic"}


def test_eval_set_values_match_taxonomy() -> None:
    rows = _rows()
    valid_tactics = {item.value for item in TacticName}
    valid_channels = {item.value for item in Channel}
    valid_categories = {item.value for item in ScamCategory}
    assert {row["channel"] for row in rows} == valid_channels
    assert {
        row["scam_category"] for row in rows if row["label"] == "scam"
    } == valid_categories

    for row in rows:
        assert row["channel"] in valid_channels
        assert row["scam_category"] in valid_categories
        assert row["has_url"] in {"true", "false"}
        tactics = set(filter(None, row["tactics"].split("|")))
        assert tactics <= valid_tactics
        if row["label"] == "scam":
            assert tactics
        else:
            assert not tactics


def test_eval_set_uses_only_reserved_identifiers() -> None:
    rows = _rows()
    for row in rows:
        urls = URL_PATTERN.findall(row["text"])
        assert (row["has_url"] == "true") == bool(urls)
        for url in urls:
            hostname = urlparse(url.rstrip(".,")).hostname or ""
            assert hostname in {"example.com", "example.org", "example.net"} or any(
                hostname.endswith(f".{domain}")
                for domain in ("example.com", "example.org", "example.net")
            )
        for phone in PHONE_PATTERN.findall(row["text"]):
            assert phone.startswith("555-01")


def test_eval_set_contains_substantial_hard_negatives() -> None:
    rows = _rows()
    hard_negatives = [
        row
        for row in rows
        if row["label"] == "legit" and row["notes"].startswith("hard_negative:")
    ]

    assert len(hard_negatives) >= 50
    combined = " ".join(row["text"].lower() for row in hard_negatives)
    for concept in ("code", "delivery", "appointment", "order", "urgent", "alert"):
        assert concept in combined

import csv
import hashlib
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from scamguard.data.eval_split import stratified_split
from scamguard.leakage import find_leaks
from scamguard.taxonomy import Channel, ScamCategory, TacticName

ROOT = Path(__file__).parents[2]
ORIGINAL = ROOT / "data" / "eval" / "test_set.csv"
DEV = ROOT / "data" / "eval" / "dev.csv"
TEST = ROOT / "data" / "eval" / "test.csv"
POOL = ROOT / "data" / "pool" / "pool.csv"
ORIGINAL_SHA256 = "b9fabc493624fc745a04c7c40620e5da552dfbc0c1932cb0be8e9a0f45ca41a3"
URL_PATTERN = re.compile(r"https?://[^\s]+")
PHONE_PATTERN = re.compile(r"\b\d{3}-\d{4}\b")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_original_eval_is_immutable() -> None:
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == ORIGINAL_SHA256


def test_split_is_deterministic_disjoint_and_stratified() -> None:
    original = _rows(ORIGINAL)
    development = _rows(DEV)
    test = _rows(TEST)
    expected_development, expected_test = stratified_split(original)

    assert len(development) == 90
    assert len(test) == 60
    assert Counter(row["label"] for row in development) == {"legit": 48, "scam": 42}
    assert Counter(row["label"] for row in test) == {"legit": 32, "scam": 28}
    assert {row["id"] for row in development}.isdisjoint(
        {row["id"] for row in test}
    )
    assert {row["id"] for row in development + test} == {
        row["id"] for row in original
    }
    assert [row["id"] for row in development] == [
        row["id"] for row in expected_development
    ]
    assert [row["id"] for row in test] == [row["id"] for row in expected_test]
    valid_channels = {item.value for item in Channel}
    assert {row["channel"] for row in development} == valid_channels
    assert {row["channel"] for row in test} == valid_channels
    scam_categories = {item.value for item in ScamCategory}
    assert {
        row["scam_category"] for row in development if row["label"] == "scam"
    } == scam_categories
    assert {
        row["scam_category"] for row in test if row["label"] == "scam"
    } == scam_categories


def test_pool_is_balanced_valid_and_fictional() -> None:
    rows = _rows(POOL)
    scams = [row for row in rows if row["label"] == "scam"]
    legitimate = [row for row in rows if row["label"] == "legit"]

    assert len(rows) >= 400
    assert len(scams) == len(legitimate) == 216
    assert set(Counter(row["scam_category"] for row in scams).values()) == {18}
    channel_counts = Counter(row["channel"] for row in rows)
    assert max(channel_counts.values()) - min(channel_counts.values()) <= 1
    assert set(channel_counts) == {item.value for item in Channel}
    observed_tactics = {
        tactic for row in scams for tactic in row["tactics"].split("|") if tactic
    }
    assert observed_tactics == {item.value for item in TacticName}
    assert all(row["notes"].startswith("hard_negative:") for row in legitimate)
    assert len({row["id"] for row in rows}) == len(rows)
    assert len({row["text"].casefold() for row in rows}) == len(rows)
    assert {row["source"] for row in rows} == {"synthetic"}

    for row in rows:
        urls = URL_PATTERN.findall(row["text"])
        assert (row["has_url"] == "true") == bool(urls)
        for url in urls:
            hostname = urlparse(url.rstrip(".,")).hostname or ""
            assert hostname.endswith(("example.com", "example.org", "example.net"))
        phones = PHONE_PATTERN.findall(row["text"])
        assert all(phone.startswith("555-01") for phone in phones)


def test_pool_has_no_eval_leakage() -> None:
    assert not find_leaks(_rows(POOL), _rows(ORIGINAL), threshold=0.88)


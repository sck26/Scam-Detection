"""Source-specific download and conversion functions."""

import bz2
import csv
import hashlib
import io
import os
import zipfile
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

import requests

from scamguard.data.schema import DatasetRecord, write_records
from scamguard.taxonomy import Channel

UCI_SMS_URL = (
    "https://archive.ics.uci.edu/static/public/228/"
    "sms+spam+collection.zip"
)
OPENPHISH_URL = "https://raw.githubusercontent.com/openphish/public_feed/main/feed.txt"
URLHAUS_URL = "https://urlhaus-api.abuse.ch/v2/files/exports/{key}/recent.csv"
PHISHTANK_URL = (
    "https://data.phishtank.com/data/{key}/online-valid.csv.bz2"
)
USER_AGENT = "ScamGuard-Research/0.1 (+local defensive research)"


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _download(url: str, destination: Path) -> bytes:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=(10, 120),
    )
    response.raise_for_status()
    content = response.content
    if not content:
        raise ValueError(f"download returned an empty file: {destination.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return content


def parse_uci_sms(content: str, collected_at: str) -> list[DatasetRecord]:
    """Parse tab-separated UCI SMS rows."""

    records: list[DatasetRecord] = []
    for index, line in enumerate(content.splitlines(), start=1):
        try:
            raw_label, text = line.split("\t", maxsplit=1)
        except ValueError as error:
            raise ValueError(f"invalid UCI SMS row {index}") from error
        if raw_label not in {"ham", "spam"} or not text.strip():
            raise ValueError(f"invalid UCI SMS values on row {index}")
        records.append(
            DatasetRecord(
                id=f"uci_sms_{index:06d}",
                text=text,
                label="scam" if raw_label == "spam" else "legit",
                channel=Channel.SMS,
                source="uci_sms_spam_collection",
                license="CC BY 4.0",
                collected_at=collected_at,
            )
        )
    return records


def download_uci_sms(raw_dir: Path, processed_dir: Path) -> int:
    """Download, verify, and normalize the UCI SMS Spam Collection."""

    archive_path = raw_dir / "uci_sms" / "sms_spam_collection.zip"
    content = _download(UCI_SMS_URL, archive_path)
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        if archive.testzip() is not None:
            raise ValueError("UCI SMS ZIP failed its integrity check")
        if "SMSSpamCollection" not in archive.namelist():
            raise ValueError("UCI SMS ZIP is missing SMSSpamCollection")
        text = archive.read("SMSSpamCollection").decode("utf-8")
    records = parse_uci_sms(text, _now())
    if len(records) != 5_574:
        raise ValueError(f"expected 5574 UCI SMS rows, found {len(records)}")
    write_records(records, processed_dir / "uci_sms.csv")
    return len(records)


def process_spearphishmx(raw_dir: Path, processed_dir: Path) -> int | None:
    """Normalize the manually downloaded sanitized email corpus."""

    source_path = raw_dir / "email" / "SpearPhishMX_dataset_publico.csv"
    if not source_path.exists():
        print(
            "SKIP SpearPhishMX: download SpearPhishMX_dataset_publico.csv from "
            "https://data.mendeley.com/datasets/h4bxjk84jb/1 and place it at "
            f"{source_path}"
        )
        return None
    records: list[DatasetRecord] = []
    collected_at = _now()
    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        required = {"asunto", "cuerpo_sanitizado", "etiqueta"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(
                "SpearPhishMX CSV must contain asunto, cuerpo_sanitizado, etiqueta"
            )
        for index, row in enumerate(reader, start=1):
            raw_label = row["etiqueta"].strip()
            if raw_label not in {"0", "1"}:
                raise ValueError(f"invalid SpearPhishMX label on row {index}")
            subject = row["asunto"].strip()
            body = row["cuerpo_sanitizado"].strip()
            text = f"{subject}\n\n{body}".strip()
            if not text:
                raise ValueError(f"empty SpearPhishMX text on row {index}")
            digest = hashlib.sha256(text.encode()).hexdigest()[:16]
            records.append(
                DatasetRecord(
                    id=f"spearphishmx_{digest}",
                    text=text,
                    label="scam" if raw_label == "1" else "legit",
                    channel=Channel.EMAIL,
                    source="spearphishmx_v1",
                    license="CC BY 4.0",
                    collected_at=collected_at,
                )
            )
    write_records(records, processed_dir / "spearphishmx.csv")
    return len(records)


def _url_records(
    urls: Iterable[str], source: str, license_name: str, collected_at: str
) -> list[DatasetRecord]:
    records: list[DatasetRecord] = []
    for url in urls:
        clean_url = url.strip()
        if not clean_url or clean_url.startswith("#"):
            continue
        digest = hashlib.sha256(clean_url.encode()).hexdigest()[:20]
        records.append(
            DatasetRecord(
                id=f"{source}_{digest}",
                text=clean_url,
                label="scam",
                channel=Channel.OTHER,
                source=source,
                license=license_name,
                collected_at=collected_at,
            )
        )
    return records


def download_openphish(raw_dir: Path, processed_dir: Path) -> int | None:
    """Download OpenPhish after explicit local acceptance of its terms."""

    if os.getenv("SCAMGUARD_ACCEPT_OPENPHISH_TERMS") != "1":
        print(
            "SKIP OpenPhish: review https://openphish.com/terms.html, then set "
            "SCAMGUARD_ACCEPT_OPENPHISH_TERMS=1 for eligible non-commercial research"
        )
        return None
    path = raw_dir / "urls" / "openphish.txt"
    content = _download(OPENPHISH_URL, path).decode("utf-8")
    records = _url_records(
        content.splitlines(),
        "openphish_community",
        "OpenPhish Terms of Use (non-commercial research only)",
        _now(),
    )
    write_records(records, processed_dir / "openphish.csv")
    return len(records)


def download_urlhaus(raw_dir: Path, processed_dir: Path) -> int | None:
    """Download the current authenticated URLhaus CSV export."""

    key = os.getenv("URLHAUS_AUTH_KEY")
    if not key:
        print(
            "SKIP URLhaus: create an Auth-Key at https://auth.abuse.ch/ and set "
            "URLHAUS_AUTH_KEY"
        )
        return None
    path = raw_dir / "urls" / "urlhaus_recent.csv"
    content = _download(URLHAUS_URL.format(key=key), path).decode("utf-8")
    rows = [line for line in content.splitlines() if not line.startswith("#")]
    reader = csv.DictReader(rows)
    if not reader.fieldnames or "url" not in reader.fieldnames:
        raise ValueError("URLhaus CSV has no url column")
    records = _url_records(
        (row["url"] for row in reader),
        "urlhaus_recent",
        "abuse.ch Community API Terms / fair use",
        _now(),
    )
    write_records(records, processed_dir / "urlhaus.csv")
    return len(records)


def download_phishtank(raw_dir: Path, processed_dir: Path) -> int | None:
    """Download the optional PhishTank verified-online feed."""

    key = os.getenv("PHISHTANK_API_KEY")
    if not key:
        print(
            "SKIP PhishTank (optional): register at https://www.phishtank.com/ "
            "and set PHISHTANK_API_KEY"
        )
        return None
    path = raw_dir / "urls" / "phishtank.csv.bz2"
    compressed = _download(PHISHTANK_URL.format(key=key), path)
    content = bz2.decompress(compressed).decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames or "url" not in reader.fieldnames:
        raise ValueError("PhishTank CSV has no url column")
    records = _url_records(
        (row["url"] for row in reader),
        "phishtank_verified",
        "PhishTank site and API terms",
        _now(),
    )
    write_records(records, processed_dir / "phishtank.csv")
    return len(records)

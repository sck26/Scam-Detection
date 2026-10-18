import csv
from pathlib import Path

from scamguard.data.schema import COLUMNS, write_records
from scamguard.data.sources import parse_uci_sms, process_spearphishmx


def test_parse_uci_sms_and_write_unified_schema(tmp_path: Path) -> None:
    records = parse_uci_sms(
        "ham\tSee you at six\nspam\tClaim a prize now", "2026-01-01Z"
    )
    output = tmp_path / "processed.csv"
    write_records(records, output)

    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert tuple(rows[0]) == COLUMNS
    assert [row["label"] for row in rows] == ["legit", "scam"]
    assert all(row["channel"] == "sms" for row in rows)


def test_process_spearphishmx_uses_sanitized_text(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    source = raw_dir / "email" / "SpearPhishMX_dataset_publico.csv"
    source.parent.mkdir(parents=True)
    source.write_text(
        "asunto;cuerpo_sanitizado;etiqueta\n"
        "Aviso;Revise [URL] de forma segura;1\n"
        "Reunión;La reunión comienza mañana;0\n",
        encoding="utf-8",
    )

    count = process_spearphishmx(raw_dir, tmp_path / "processed")

    assert count == 2
    output = (tmp_path / "processed" / "spearphishmx.csv").read_text()
    assert "[URL]" in output
    assert "scam" in output
    assert "legit" in output

"""Persistent cache for validated structured model responses."""

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class ResponseCache:
    """SQLite cache keyed by model, prompt version, and normalized text."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS responses (
                    cache_key TEXT PRIMARY KEY,
                    model TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    text_hash TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def key(model: str, prompt_version: str, normalized_text: str) -> str:
        payload = json.dumps(
            [model, prompt_version, normalized_text],
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def get(self, model: str, prompt_version: str, normalized_text: str) -> str | None:
        cache_key = self.key(model, prompt_version, normalized_text)
        with sqlite3.connect(self.path) as connection:
            row = connection.execute(
                "SELECT response FROM responses WHERE cache_key = ?", (cache_key,)
            ).fetchone()
        return str(row[0]) if row else None

    def put(
        self,
        model: str,
        prompt_version: str,
        normalized_text: str,
        response: str,
    ) -> None:
        cache_key = self.key(model, prompt_version, normalized_text)
        text_hash = hashlib.sha256(normalized_text.encode()).hexdigest()
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO responses
                (cache_key, model, prompt_version, text_hash, response, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    cache_key,
                    model,
                    prompt_version,
                    text_hash,
                    response,
                    datetime.now(UTC).isoformat(),
                ),
            )


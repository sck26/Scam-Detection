"""Shared safety and parsing helpers for local HTTP model servers."""

from typing import Any
from urllib.parse import urlparse


def require_loopback_url(url: str) -> str:
    """Reject accidental transmission of messages to a remote service."""

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("model server URL must use HTTP or HTTPS")
    if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("model server must be loopback-only for Phase 1")
    return url.rstrip("/")


def optional_int(value: Any) -> int | None:
    return int(value) if isinstance(value, int | float) else None


def throughput(tokens: int | None, seconds: float) -> float | None:
    if tokens is None or seconds <= 0:
        return None
    return tokens / seconds


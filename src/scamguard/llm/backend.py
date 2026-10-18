"""Backend-neutral local LLM request and response types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LLMRequest:
    """One structured generation request."""

    system_prompt: str
    user_prompt: str
    json_schema: dict[str, Any]
    prompt_version: str
    normalized_text: str


@dataclass(frozen=True, slots=True)
class LLMResponse:
    """Raw backend response and measured generation statistics."""

    content: str
    model: str
    latency_seconds: float
    input_tokens: int | None
    output_tokens: int | None
    tokens_per_second: float | None
    cached: bool = False


class LLMBackend(ABC):
    """Interface for local structured-generation servers and runtimes."""

    model: str

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate one response without interpreting its content."""


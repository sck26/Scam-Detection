"""Environment-driven local backend configuration and factory."""

import os
from dataclasses import dataclass
from pathlib import Path

from scamguard.llm.backend import LLMBackend
from scamguard.llm.huggingface import HuggingFaceBackend
from scamguard.llm.ollama import OllamaBackend
from scamguard.llm.openai_compat import OpenAICompatibleBackend


@dataclass(frozen=True, slots=True)
class BackendSettings:
    backend: str = "ollama"
    model: str = ""
    ollama_url: str = "http://127.0.0.1:11434"
    openai_base_url: str = "http://127.0.0.1:8000/v1"
    openai_api_key: str | None = None
    hf_device: str = "cpu"
    cache_path: Path = Path("data/cache/llm.sqlite3")
    retries: int = 2

    @classmethod
    def from_env(cls) -> "BackendSettings":
        backend = os.getenv("SCAMGUARD_LLM_BACKEND", "ollama")
        default_model = (
            os.getenv("SCAMGUARD_HF_MODEL", "")
            if backend == "huggingface"
            else ""
        )
        model = os.getenv("SCAMGUARD_LLM_MODEL", default_model)
        return cls(
            backend=backend,
            model=model,
            ollama_url=os.getenv(
                "SCAMGUARD_OLLAMA_URL", "http://127.0.0.1:11434"
            ),
            openai_base_url=os.getenv(
                "SCAMGUARD_OPENAI_BASE_URL", "http://127.0.0.1:8000/v1"
            ),
            openai_api_key=os.getenv("SCAMGUARD_OPENAI_API_KEY"),
            hf_device=os.getenv("SCAMGUARD_HF_DEVICE", "cpu"),
            cache_path=Path(
                os.getenv("SCAMGUARD_LLM_CACHE", "data/cache/llm.sqlite3")
            ),
            retries=int(os.getenv("SCAMGUARD_LLM_RETRIES", "2")),
        )


def create_backend(settings: BackendSettings) -> LLMBackend:
    """Instantiate the configured backend without loading model weights."""

    if not settings.model:
        raise ValueError("SCAMGUARD_LLM_MODEL must name a local model")
    if settings.backend == "ollama":
        return OllamaBackend(settings.model, settings.ollama_url)
    if settings.backend == "huggingface":
        return HuggingFaceBackend(settings.model, settings.hf_device)
    if settings.backend == "openai-compatible":
        return OpenAICompatibleBackend(
            settings.model,
            settings.openai_base_url,
            settings.openai_api_key,
        )
    raise ValueError(f"unknown local LLM backend: {settings.backend}")

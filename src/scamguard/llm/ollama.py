"""Ollama local HTTP backend with native JSON-schema constraints."""

from time import perf_counter
from typing import Any

import requests

from scamguard.llm.backend import LLMBackend, LLMRequest, LLMResponse
from scamguard.llm.http import optional_int, require_loopback_url, throughput


class OllamaBackend(LLMBackend):
    """Generate through Ollama's loopback chat API."""

    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 180.0,
        session: requests.Session | None = None,
    ) -> None:
        self.model = model
        self.base_url = require_loopback_url(base_url)
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "stream": False,
            "think": False,
            "format": request.json_schema,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "options": {"temperature": 0, "num_predict": 384},
        }
        started = perf_counter()
        response = self.session.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        latency = perf_counter() - started
        body = response.json()
        content = body.get("message", {}).get("content")
        if not isinstance(content, str):
            raise ValueError("Ollama response has no message content")
        input_tokens = optional_int(body.get("prompt_eval_count"))
        output_tokens = optional_int(body.get("eval_count"))
        duration_ns = body.get("eval_duration")
        generation_seconds = (
            float(duration_ns) / 1_000_000_000
            if isinstance(duration_ns, int | float) and duration_ns > 0
            else latency
        )
        return LLMResponse(
            content=content,
            model=self.model,
            latency_seconds=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            tokens_per_second=throughput(output_tokens, generation_seconds),
        )

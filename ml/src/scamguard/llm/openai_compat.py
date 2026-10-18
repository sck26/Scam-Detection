"""Loopback-only OpenAI-compatible chat-completions backend."""

from time import perf_counter
from typing import Any

import requests

from scamguard.llm.backend import LLMBackend, LLMRequest, LLMResponse
from scamguard.llm.http import optional_int, require_loopback_url, throughput


class OpenAICompatibleBackend(LLMBackend):
    """Use a local server implementing the OpenAI chat-completions contract."""

    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:8000/v1",
        api_key: str | None = None,
        timeout_seconds: float = 180.0,
        session: requests.Session | None = None,
    ) -> None:
        self.model = model
        self.base_url = require_loopback_url(base_url)
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "scamguard_detection",
                    "strict": True,
                    "schema": request.json_schema,
                },
            },
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        started = perf_counter()
        response = self.session.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        latency = perf_counter() - started
        body = response.json()
        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ValueError("OpenAI-compatible response has no content") from error
        if not isinstance(content, str):
            raise ValueError("OpenAI-compatible content is not text")
        usage = body.get("usage", {})
        input_tokens = optional_int(usage.get("prompt_tokens"))
        output_tokens = optional_int(usage.get("completion_tokens"))
        return LLMResponse(
            content=content,
            model=self.model,
            latency_seconds=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            tokens_per_second=throughput(output_tokens, latency),
        )


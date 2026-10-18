import json
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

from scamguard.llm.backend import LLMBackend, LLMRequest, LLMResponse
from scamguard.llm.cache import ResponseCache
from scamguard.llm.http import require_loopback_url
from scamguard.llm.ollama import OllamaBackend
from scamguard.llm.runner import StructuredRunner


class ExampleOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict: str
    score: float


class FakeBackend(LLMBackend):
    model = "fake-local"

    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        content = self.responses.pop(0)
        return LLMResponse(content, self.model, 0.2, 10, 5, 25.0)


def _request() -> LLMRequest:
    return LLMRequest(
        system_prompt="system",
        user_prompt="message",
        json_schema=ExampleOutput.model_json_schema(),
        prompt_version="v1",
        normalized_text="message",
    )


def test_structured_runner_repairs_then_caches(tmp_path: Path) -> None:
    backend = FakeBackend(
        ["not json", json.dumps({"verdict": "safe", "score": 0.1})]
    )
    runner = StructuredRunner(
        backend, ExampleOutput, ResponseCache(tmp_path / "cache.sqlite3")
    )

    first = runner.run(_request())
    second = runner.run(_request())

    assert first.ok
    assert first.attempts == 2
    assert len(backend.calls) == 2
    assert "previous response was invalid" in backend.calls[1].user_prompt
    assert second.ok
    assert second.response.cached
    assert len(backend.calls) == 2


def test_structured_runner_returns_explicit_error(tmp_path: Path) -> None:
    backend = FakeBackend(["{}", "still invalid"])
    runner = StructuredRunner(
        backend,
        ExampleOutput,
        ResponseCache(tmp_path / "cache.sqlite3"),
        max_retries=1,
    )

    result = runner.run(_request())

    assert not result.ok
    assert result.value is None
    assert result.error is not None and result.error.startswith("ERROR:")
    assert result.attempts == 2


@pytest.mark.parametrize(
    "url",
    [
        "https://api.example.com/v1",
        "http://192.0.2.1:8000",
        "file:///tmp/model",
    ],
)
def test_remote_model_servers_are_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        require_loopback_url(url)


def test_loopback_model_servers_are_allowed() -> None:
    assert require_loopback_url("http://127.0.0.1:11434/") == (
        "http://127.0.0.1:11434"
    )


class FakeHTTPResponse:
    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict[str, object]:
        return {
            "message": {"content": '{"verdict":"safe","score":0.1}'},
            "prompt_eval_count": 10,
            "eval_count": 5,
            "eval_duration": 1_000_000_000,
        }


class FakeSession:
    def __init__(self) -> None:
        self.payload: dict[str, object] | None = None

    def post(
        self, url: str, json: dict[str, object], timeout: float
    ) -> FakeHTTPResponse:
        assert url == "http://127.0.0.1:11434/api/chat"
        assert timeout == 180.0
        self.payload = json
        return FakeHTTPResponse()


def test_ollama_disables_hidden_thinking_and_caps_generation() -> None:
    session = FakeSession()
    backend = OllamaBackend("fake", session=session)  # type: ignore[arg-type]

    response = backend.generate(_request())

    assert response.output_tokens == 5
    assert session.payload is not None
    assert session.payload["think"] is False
    assert session.payload["options"] == {"temperature": 0, "num_predict": 384}

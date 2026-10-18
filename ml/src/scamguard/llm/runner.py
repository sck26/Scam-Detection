"""Validated structured generation with repair retries and explicit errors."""

import json
from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

from scamguard.llm.backend import LLMBackend, LLMRequest, LLMResponse
from scamguard.llm.cache import ResponseCache

SchemaT = TypeVar("SchemaT", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class StructuredRunResult(Generic[SchemaT]):
    """Validated data or an explicit parsing/generation error."""

    value: SchemaT | None
    error: str | None
    attempts: int
    response: LLMResponse

    @property
    def ok(self) -> bool:
        return self.value is not None and self.error is None


class StructuredRunner(Generic[SchemaT]):
    """Run a backend until output validates or the retry budget is exhausted."""

    def __init__(
        self,
        backend: LLMBackend,
        schema: type[SchemaT],
        cache: ResponseCache,
        max_retries: int = 2,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries cannot be negative")
        self.backend = backend
        self.schema = schema
        self.cache = cache
        self.max_retries = max_retries

    def _validate(self, content: str) -> SchemaT:
        payload = json.loads(content)
        return self.schema.model_validate(payload)

    def run(self, request: LLMRequest) -> StructuredRunResult[SchemaT]:
        cached = self.cache.get(
            self.backend.model, request.prompt_version, request.normalized_text
        )
        if cached is not None:
            try:
                value = self._validate(cached)
            except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
                cached = None
            else:
                response = LLMResponse(
                    content=cached,
                    model=self.backend.model,
                    latency_seconds=0.0,
                    input_tokens=None,
                    output_tokens=None,
                    tokens_per_second=None,
                    cached=True,
                )
                return StructuredRunResult(value, None, 0, response)

        current = request
        last_response: LLMResponse | None = None
        last_error = "unknown structured output error"
        for attempt in range(1, self.max_retries + 2):
            try:
                last_response = self.backend.generate(current)
                value = self._validate(last_response.content)
            except (
                json.JSONDecodeError,
                ValidationError,
                TypeError,
                ValueError,
            ) as error:
                last_error = f"{type(error).__name__}: {error}"
                if attempt <= self.max_retries:
                    repair = (
                        "Your previous response was invalid. Return only JSON "
                        "matching the "
                        f"provided schema. Validation error: {last_error}"
                    )
                    current = LLMRequest(
                        system_prompt=current.system_prompt,
                        user_prompt=f"{current.user_prompt}\n\n{repair}",
                        json_schema=current.json_schema,
                        prompt_version=current.prompt_version,
                        normalized_text=current.normalized_text,
                    )
                continue
            self.cache.put(
                self.backend.model,
                request.prompt_version,
                request.normalized_text,
                last_response.content,
            )
            return StructuredRunResult(value, None, attempt, last_response)

        if last_response is None:
            last_response = LLMResponse(
                content="",
                model=self.backend.model,
                latency_seconds=0.0,
                input_tokens=None,
                output_tokens=None,
                tokens_per_second=None,
            )
        return StructuredRunResult(
            value=None,
            error=f"ERROR: structured output failed after retries: {last_error}",
            attempts=self.max_retries + 1,
            response=last_response,
        )

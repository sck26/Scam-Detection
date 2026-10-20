"""Tactic-based structured detector powered by a local LLM backend."""

from dataclasses import replace
from pathlib import Path

from scamguard.leakage import normalize_text
from scamguard.llm.backend import LLMBackend, LLMRequest
from scamguard.llm.cache import ResponseCache
from scamguard.llm.otp_guard import review_otp_message
from scamguard.llm.prompting import PromptBundle, build_prompt, message_prompt
from scamguard.llm.runner import StructuredRunner, StructuredRunResult
from scamguard.llm.schema import DetectionOutput


class LocalLLMDetector:
    """Run the product detection contract through a validated local backend."""

    def __init__(
        self,
        backend: LLMBackend,
        cache_path: Path,
        prompt_version: str = "v2",
        pool_path: Path = Path("data/pool/pool.csv"),
        few_shot_count: int = 6,
        max_retries: int = 2,
    ) -> None:
        self.prompt: PromptBundle = build_prompt(
            prompt_version, pool_path, few_shot_count
        )
        self.runner = StructuredRunner(
            backend,
            DetectionOutput,
            ResponseCache(cache_path),
            max_retries,
        )

    def detect(self, text: str) -> StructuredRunResult[DetectionOutput]:
        if not text.strip():
            raise ValueError("message text cannot be empty")
        request = LLMRequest(
            system_prompt=self.prompt.system_prompt,
            user_prompt=message_prompt(text),
            json_schema=DetectionOutput.model_json_schema(),
            prompt_version=self.prompt.cache_version,
            normalized_text=normalize_text(text),
        )
        result = self.runner.run(request)
        # v2 is frozen for historical experiments. v3 opts into the new guard;
        # errors still remain errors (no silent fallback to SAFE).
        if self.prompt.version == "v3" and result.ok and result.value is not None:
            return replace(result, value=review_otp_message(text, result.value))
        return result

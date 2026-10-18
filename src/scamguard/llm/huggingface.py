"""Lazy, local-files-only Hugging Face transformers backend."""

import importlib
from time import perf_counter
from typing import Any

from scamguard.llm.backend import LLMBackend, LLMRequest, LLMResponse
from scamguard.llm.http import throughput


class HuggingFaceBackend(LLMBackend):
    """Run a previously downloaded causal language model locally."""

    def __init__(
        self,
        model: str,
        device: str = "cpu",
        max_new_tokens: int = 512,
    ) -> None:
        self.model = model
        self.device = device
        self.max_new_tokens = max_new_tokens
        self._tokenizer: Any = None
        self._model: Any = None

    def _load(self) -> tuple[Any, Any]:
        if self._tokenizer is None or self._model is None:
            try:
                transformers = importlib.import_module("transformers")
            except ImportError as error:
                raise RuntimeError(
                    "Hugging Face backend needs: pip install -e '.[models]'"
                ) from error
            self._tokenizer = transformers.AutoTokenizer.from_pretrained(
                self.model,
                local_files_only=True,
            )
            self._model = transformers.AutoModelForCausalLM.from_pretrained(
                self.model,
                local_files_only=True,
            ).to(self.device)
        return self._tokenizer, self._model

    def generate(self, request: LLMRequest) -> LLMResponse:
        tokenizer, model = self._load()
        messages = [
            {"role": "system", "content": request.system_prompt},
            {"role": "user", "content": request.user_prompt},
        ]
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        encoded = tokenizer(prompt, return_tensors="pt")
        encoded = {name: value.to(self.device) for name, value in encoded.items()}
        input_tokens = int(encoded["input_ids"].shape[-1])
        started = perf_counter()
        generated = model.generate(
            **encoded,
            do_sample=False,
            max_new_tokens=self.max_new_tokens,
        )
        latency = perf_counter() - started
        output_ids = generated[0][input_tokens:]
        content = str(tokenizer.decode(output_ids, skip_special_tokens=True))
        output_tokens = int(output_ids.shape[-1])
        return LLMResponse(
            content=content,
            model=self.model,
            latency_seconds=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            tokens_per_second=throughput(output_tokens, latency),
        )


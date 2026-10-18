import json
from pathlib import Path

import pytest

from scamguard.llm.backend import LLMBackend, LLMRequest, LLMResponse
from scamguard.llm.detector import LocalLLMDetector
from scamguard.llm.prompting import build_prompt, select_few_shots
from scamguard.llm.schema import DetectionOutput
from scamguard.taxonomy import TacticName


class ValidBackend(LLMBackend):
    model = "mock-local"

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "danger_level": "safe",
            "score": 0.02,
            "tactics": [],
            "scam_category": "other",
            "red_flags": [],
            "recommended_action": "No action is needed.",
            "legit_signals": ["No request for money or credentials."],
        }
        return LLMResponse(json.dumps(payload), self.model, 0.1, 10, 10, 100.0)


def test_detection_schema_restricts_tactics_and_score() -> None:
    with pytest.raises(ValueError):
        DetectionOutput.model_validate(
            {
                "danger_level": "safe",
                "score": 1.5,
                "tactics": ["made_up"],
                "scam_category": "other",
                "red_flags": [],
                "recommended_action": "No action is needed.",
                "legit_signals": [],
            }
        )


def test_prompt_is_taxonomy_driven_and_hashed() -> None:
    prompt = build_prompt("v1", few_shot_count=0)

    assert all(tactic.value in prompt.system_prompt for tactic in TacticName)
    assert "Genuine bank alerts" in prompt.system_prompt
    assert len(prompt.sha256) == 64
    assert not prompt.few_shot_ids


def test_few_shots_are_pool_only_and_cover_both_labels() -> None:
    rows = select_few_shots(Path("data/pool/pool.csv"), 8)

    assert len(rows) == 8
    assert {row["label"] for row in rows} == {"scam", "legit"}
    assert all(row["id"].startswith("pool_") for row in rows)
    assert all(
        "hard_negative" in row["notes"]
        for row in rows
        if row["label"] == "legit"
    )


def test_detector_uses_prompt_hash_in_cache_identity(tmp_path: Path) -> None:
    detector = LocalLLMDetector(
        ValidBackend(),
        tmp_path / "cache.sqlite3",
        prompt_version="v2",
        few_shot_count=4,
    )

    first = detector.detect("Your appointment is tomorrow at noon.")
    second = detector.detect("Your appointment is tomorrow at noon.")

    assert first.ok
    assert second.response.cached
    assert detector.prompt.cache_version.startswith("v2:")

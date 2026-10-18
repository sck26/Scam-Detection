import pytest

from scamguard.final_eval import calibrate, load_frozen_config
from scamguard.llm.prompting import build_prompt


def test_frozen_config_matches_prompt_before_final() -> None:
    config = load_frozen_config()
    prompt = build_prompt(config.prompt_version, few_shot_count=config.few_shot_count)

    assert prompt.sha256 == config.prompt_sha256
    assert prompt.few_shot_ids == config.few_shot_ids


def test_frozen_platt_calibration_known_value() -> None:
    config = load_frozen_config()

    assert calibrate(0.0, config) == pytest.approx(0.108233, abs=1e-6)
    assert calibrate(1.0, config) == pytest.approx(0.918277, abs=1e-6)

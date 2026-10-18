from pathlib import Path

import pytest

from scamguard.taxonomy import (
    Channel,
    DangerLevel,
    DuplicateKeyError,
    ScamCategory,
    TacticName,
    load_taxonomy,
)


def test_bundled_taxonomy_is_complete_and_valid() -> None:
    taxonomy = load_taxonomy()

    assert set(taxonomy.danger_levels) == set(DangerLevel)
    assert set(taxonomy.channels) == set(Channel)
    assert set(taxonomy.tactics) == set(TacticName)
    assert set(taxonomy.categories) == set(ScamCategory)
    assert all(len(tactic.examples) == 2 for tactic in taxonomy.tactics.values())


def test_duplicate_yaml_keys_are_rejected(tmp_path: Path) -> None:
    duplicate_yaml = tmp_path / "duplicate.yaml"
    duplicate_yaml.write_text(
        "danger_levels: [safe]\ndanger_levels: [dangerous]\n",
        encoding="utf-8",
    )

    with pytest.raises(DuplicateKeyError, match="danger_levels"):
        load_taxonomy(duplicate_yaml)


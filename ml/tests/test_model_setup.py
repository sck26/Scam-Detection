import subprocess
from pathlib import Path

import pytest

from scamguard.hardware import inspect_hardware
from scamguard.model_setup import load_manifest, pull_models


def test_manifest_has_small_and_mid_candidates() -> None:
    manifest = load_manifest()

    assert len(manifest.models) >= 3
    assert {model.role for model in manifest.models} >= {"small", "mid"}
    assert all(model.quantization == "Q4_K_M" for model in manifest.models)
    assert all(model.license == "Apache-2.0" for model in manifest.models)


def test_pull_uses_exact_manifest_tags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr("scamguard.model_setup.shutil.which", lambda _: "/bin/ollama")

    def fake_run(command: list[str], check: bool) -> subprocess.CompletedProcess[str]:
        assert check
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("scamguard.model_setup.subprocess.run", fake_run)
    manifest = load_manifest()
    pull_models(manifest)

    assert calls == [["ollama", "pull", model.tag] for model in manifest.models]


def test_hardware_inventory_contains_no_device_identifiers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    info = inspect_hardware()

    assert set(info) == {
        "os",
        "architecture",
        "chip",
        "cpu_cores",
        "memory_gb",
        "apple_silicon",
        "disk_free_gb",
    }


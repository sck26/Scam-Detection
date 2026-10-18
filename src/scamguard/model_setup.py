"""Inspect and pull the exact local Ollama candidates."""

import argparse
import shutil
import subprocess
from importlib.resources import files
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CandidateModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    role: str
    tag: str
    parameters: str
    size_gb: float = Field(gt=0)
    quantization: str
    license: str
    source: HttpUrl


class ModelManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    models: tuple[CandidateModel, ...]


def load_manifest() -> ModelManifest:
    path = files("scamguard").joinpath("models.yaml")
    raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ModelManifest.model_validate(raw)


def pull_models(manifest: ModelManifest) -> None:
    """Pull candidates sequentially, failing immediately on an Ollama error."""

    if shutil.which("ollama") is None:
        raise SystemExit(
            "Ollama is missing. Install from https://ollama.com/download, start it, "
            "then rerun `make models`."
        )
    for model in manifest.models:
        print(f"Pulling {model.tag} ({model.size_gb:.1f} GB, {model.quantization})")
        subprocess.run(["ollama", "pull", model.tag], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage local candidate models")
    parser.add_argument(
        "--list",
        action="store_true",
        help="show pinned candidates without downloading them",
    )
    args = parser.parse_args()
    manifest = load_manifest()
    if args.list:
        for model in manifest.models:
            print(
                f"{model.role:5} {model.tag:37} {model.size_gb:>4.1f} GB "
                f"{model.quantization} {model.license}"
            )
        return
    pull_models(manifest)


if __name__ == "__main__":
    main()


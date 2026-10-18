"""Quick local command-line scam detection."""

import argparse
import json
from dataclasses import replace
from pathlib import Path

from scamguard.llm.config import BackendSettings, create_backend
from scamguard.llm.detector import LocalLLMDetector
from scamguard.llm.prompting import available_prompt_versions


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze one message locally")
    parser.add_argument("text", help="message text to analyze")
    parser.add_argument("--model", required=True, help="installed local model name")
    parser.add_argument(
        "--prompt",
        choices=available_prompt_versions(),
        default="v2",
    )
    parser.add_argument("--few-shot-count", type=int, default=6)
    parser.add_argument("--pool", type=Path, default=Path("data/pool/pool.csv"))
    parser.add_argument("--json", action="store_true", help="print JSON only")
    return parser


def main() -> None:
    args = _parser().parse_args()
    settings = replace(BackendSettings.from_env(), model=args.model)
    detector = LocalLLMDetector(
        create_backend(settings),
        settings.cache_path,
        prompt_version=args.prompt,
        pool_path=args.pool,
        few_shot_count=args.few_shot_count,
        max_retries=settings.retries,
    )
    result = detector.detect(args.text)
    if not result.ok or result.value is None:
        payload = {"status": "error", "error": result.error}
        print(json.dumps(payload, indent=2))
        raise SystemExit(2)

    output = result.value
    if args.json:
        print(output.model_dump_json(indent=2))
        return
    tactics = ", ".join(item.value for item in output.tactics) or "none"
    print(f"Verdict: {output.danger_level.value.upper()} ({output.score:.0%})")
    print(f"Category: {output.scam_category.value}")
    print(f"Tactics: {tactics}")
    if output.red_flags:
        print("Red flags: " + "; ".join(output.red_flags))
    if output.legit_signals:
        print("Legitimate signals: " + "; ".join(output.legit_signals))
    print(f"Recommended action: {output.recommended_action}")
    print(
        f"Model: {result.response.model}; prompt: {detector.prompt.version} "
        f"({detector.prompt.sha256[:12]}); latency: "
        f"{result.response.latency_seconds:.3f}s"
    )
    print("\nJSON:")
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()


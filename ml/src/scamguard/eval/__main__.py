"""Command-line evaluation harness."""

import argparse
from collections.abc import Callable
from pathlib import Path

from scamguard.eval.detectors import (
    AlwaysScamDetector,
    Detector,
    RandomDetector,
    TfidfLogisticDetector,
)
from scamguard.eval.report import evaluate_detector, load_evaluation_rows, write_reports


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate ScamGuard detectors")
    parser.add_argument(
        "--model",
        choices=("always-scam", "random", "tfidf", "all"),
        required=True,
    )
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--train-data", type=Path, default=Path("data/processed"))
    parser.add_argument("--max-fpr", type=float, default=0.05)
    return parser.parse_args()


def main() -> None:
    """Evaluate selected detectors and write reports."""

    args = _arguments()
    if not 0.0 <= args.max_fpr <= 1.0:
        raise SystemExit("--max-fpr must be between 0 and 1")
    detector_factories: dict[str, Callable[[], Detector]] = {
        "always-scam": AlwaysScamDetector,
        "random": RandomDetector,
        "tfidf": lambda: TfidfLogisticDetector(args.train_data),
    }
    names = tuple(detector_factories) if args.model == "all" else (args.model,)
    detectors: list[Detector] = [detector_factories[name]() for name in names]
    rows = load_evaluation_rows(args.data)
    results = [
        evaluate_detector(detector, rows, args.max_fpr) for detector in detectors
    ]
    json_path, markdown_path = write_reports(
        results, args.data, args.out, args.max_fpr, len(rows)
    )
    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")


if __name__ == "__main__":
    main()

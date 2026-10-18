"""Render the frozen TEST result without recomputing it."""

import argparse
import json
from pathlib import Path
from typing import Any


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _ci(value: dict[str, float]) -> str:
    return f"{_pct(value['low'])}-{_pct(value['high'])}"


def render_final_report(report: dict[str, Any]) -> str:
    llm = report["models"][0]
    llm_metrics = llm["metrics"]
    primary_met = (
        llm_metrics["recall"] >= 0.90
        and llm_metrics["false_positive_rate"] <= 0.05
    )
    preferred_met = llm_metrics["false_positive_rate"] <= 0.03
    lines = [
        "# Phase 1 final held-out evaluation",
        "",
        f"Generated: {report['generated_at']}",
        f"Data: `{report['data']}` ({report['examples']} locked TEST examples)",
        "",
        "The configuration was frozen from DEV before this single audited TEST run. "
        "No thresholds, prompt text, examples, or calibration parameters were changed "
        "after TEST was viewed.",
        "",
        "## Result",
        "",
        "| Model | Precision | Recall | F1 | FPR | Accuracy | 95% recall CI | "
        "95% FPR CI |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for model in report["models"]:
        metrics = model["metrics"]
        intervals = model["confidence_intervals_95"]
        lines.append(
            f"| {model['name']} | {_pct(metrics['precision'])} | "
            f"{_pct(metrics['recall'])} | {_pct(metrics['f1'])} | "
            f"{_pct(metrics['false_positive_rate'])} | "
            f"{_pct(metrics['accuracy'])} | {_ci(intervals['recall'])} | "
            f"{_ci(intervals['false_positive_rate'])} |"
        )
    matrix = llm_metrics["confusion_matrix"]
    lines.extend(
        [
            "",
            "The primary target (recall >= 90% at FPR <= 5%) was "
            f"{'met' if primary_met else 'not met'}. The preferred FPR <= 3% was "
            f"{'met' if preferred_met else 'not met'}: one false positive among 32 "
            "legitimate messages is 3.125%.",
            "",
            f"Frozen LLM confusion matrix: TN={matrix['tn']}, FP={matrix['fp']}, "
            f"FN={matrix['fn']}, TP={matrix['tp']}. Structured-output errors: "
            f"{llm['errors']}.",
            "",
            f"Median latency was {llm['performance']['median_latency_seconds']:.3f}s; "
            f"P95 was {llm['performance']['p95_latency_seconds']:.3f}s; mean "
            "generation "
            f"throughput was {llm['performance']['mean_tokens_per_second']:.1f} tok/s.",
            "",
            "## Frozen identity",
            "",
            f"- Model: `{llm['model']}`",
            f"- Prompt: {llm['prompt_version']} / `{llm['prompt_sha256']}`",
            f"- Dangerous threshold: "
            f"{llm['thresholds']['dangerous_at_or_above']:.15f}",
            "- Calibration: DEV-fitted Platt scaling, coefficient "
            f"{llm['calibration']['coefficient']:.15f}, intercept "
            f"{llm['calibration']['intercept']:.15f}",
            "",
            "## Frozen LLM per-category results",
            "",
            "| Category | N | Precision | Recall | FPR |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for category, values in llm["per_category"].items():
        lines.append(
            f"| {category} | {values['count']} | {_pct(values['precision'])} | "
            f"{_pct(values['recall'])} | {_pct(values['false_positive_rate'])} |"
        )
    lines.extend(
        [
            "",
            "## Final error analysis",
            "",
            "There were no false negatives. The single false positive was `eval_090`, "
            "a genuine sign-in approval code that tells the user to deny an unfamiliar "
            "request inside the app. As on DEV, the model returned all ten tactics but "
            "an empty red-flag list. This confirms the need for an "
            "evidence-consistency "
            "validator and more genuine 2FA hard negatives; it does not justify a "
            "post-TEST threshold change.",
            "",
            "The 95% intervals are wide because TEST contains only 28 scams and 32 "
            "legitimate messages. The observed target pass should therefore be treated "
            "as promising, not production validation.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render frozen TEST Markdown")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.write_text(render_final_report(report), encoding="utf-8")


if __name__ == "__main__":
    main()

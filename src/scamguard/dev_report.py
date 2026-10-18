"""Render the complete human-readable DEV experiment report."""

import argparse
import json
from pathlib import Path
from typing import Any


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _ci(interval: dict[str, float]) -> str:
    return f"{_pct(interval['low'])}-{_pct(interval['high'])}"


def render_dev_report(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 1 DEV model experiments",
        "",
        f"Generated: {report['generated_at']}",
        f"Data: `{report['data']}` (DEV only; TEST remained locked)",
        "",
        "Platt scaling and all thresholds were fit on DEV. Confidence intervals are "
        "95% Wilson intervals. These are model-selection results, not unbiased final "
        "generalization estimates.",
        "",
        "## Comparison",
        "",
        "| Model | Prompt | P | R | F1 | FPR | Errors | Median | P95 | tok/s |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in report["results"]:
        metrics = result["metrics"]
        performance = result["performance"]
        lines.append(
            f"| `{result['model']}` | {result['prompt_version']} | "
            f"{_pct(metrics['precision'])} | {_pct(metrics['recall'])} | "
            f"{_pct(metrics['f1'])} | {_pct(metrics['false_positive_rate'])} | "
            f"{result['errors']} | {performance['median_latency_seconds']:.2f}s | "
            f"{performance['p95_latency_seconds']:.2f}s | "
            f"{performance['mean_tokens_per_second']:.1f} |"
        )
    lines.extend(
        [
            "",
            "## Frozen selection for final evaluation",
            "",
            "`qwen3:4b-instruct-2507-q4_K_M` with prompt v2 was selected because it "
            "maximized recall under the 5% FPR constraint. It returned 42/42 scam "
            "messages and flagged 1/48 legitimate messages on DEV. No third prompt "
            "iteration was performed.",
            "",
            "Its frozen prompt SHA-256 and calibrated thresholds are recorded "
            "below and "
            "must not be changed after viewing TEST.",
        ]
    )
    for result in report["results"]:
        metrics = result["metrics"]
        intervals = result["confidence_intervals_95"]
        matrix = metrics["confusion_matrix"]
        thresholds = result["thresholds"]
        lines.extend(
            [
                "",
                f"## {result['model']} / {result['prompt_version']}",
                "",
                f"Prompt SHA-256: `{result['prompt_sha256']}`. Few-shot examples: "
                f"{result['few_shot_count']} "
                f"({', '.join(result['few_shot_ids']) or 'none'}).",
                f"Valid responses: {result['valid_responses']}/{result['examples']}; "
                f"explicit errors: {result['errors']}.",
                "Confusion matrix at the selected dangerous threshold: "
                f"TN={matrix['tn']}, "
                f"FP={matrix['fp']}, FN={matrix['fn']}, TP={matrix['tp']}.",
                f"Precision {_pct(metrics['precision'])} "
                f"(CI {_ci(intervals['precision'])}); "
                f"recall {_pct(metrics['recall'])} (CI {_ci(intervals['recall'])}); "
                f"F1 {_pct(metrics['f1'])}; FPR "
                f"{_pct(metrics['false_positive_rate'])} (CI "
                f"{_ci(intervals['false_positive_rate'])}).",
                f"Frozen mapping: safe below {thresholds['safe_below']:.6f}; "
                "suspicious "
                f"below {thresholds['suspicious_below']:.6f}; dangerous at or above "
                f"{thresholds['dangerous_at_or_above']:.6f}.",
                "",
                "### Reliability after DEV Platt scaling",
                "",
                "| Score bin | Count | Mean score | Observed scam rate |",
                "|---|---:|---:|---:|",
            ]
        )
        for item in result["calibration"]["reliability"]:
            mean_score = (
                _pct(item["mean_score"]) if item["mean_score"] is not None else "—"
            )
            observed = (
                _pct(item["observed_scam_rate"])
                if item["observed_scam_rate"] is not None
                else "—"
            )
            lines.append(
                f"| {_pct(item['range'][0])}-{_pct(item['range'][1])} | "
                f"{item['count']} | {mean_score} | {observed} |"
            )
        for heading, key in (
            ("Per-category", "per_category"),
            ("Per-channel", "per_channel"),
        ):
            lines.extend(
                [
                    "",
                    f"### {heading}",
                    "",
                    "| Group | N | Precision | Recall | FPR |",
                    "|---|---:|---:|---:|---:|",
                ]
            )
            for group, values in result[key].items():
                lines.append(
                    f"| {group} | {values['count']} | {_pct(values['precision'])} | "
                    f"{_pct(values['recall'])} | "
                    f"{_pct(values['false_positive_rate'])} |"
                )
        lines.extend(
            [
                "",
                "### Tactic extraction",
                "",
                "| Tactic | Support | Precision | Recall |",
                "|---|---:|---:|---:|",
            ]
        )
        for tactic, values in result["tactic_metrics"].items():
            lines.append(
                f"| {tactic} | {values['support']} | "
                f"{_pct(values['precision'])} | {_pct(values['recall'])} |"
            )
        false_positives = [
            item["id"]
            for item in result["predictions"]
            if item["actual"] == "legit" and item["predicted"] == "scam"
        ]
        false_negatives = [
            item["id"]
            for item in result["predictions"]
            if item["actual"] == "scam" and item["predicted"] == "legit"
        ]
        lines.extend(
            [
                "",
                "### Errors",
                "",
                f"False positives: {', '.join(false_positives) or 'none'}.",
                f"False negatives: {', '.join(false_negatives) or 'none'}.",
            ]
        )
    lines.extend(
        [
            "",
            "## Written error analysis",
            "",
            "The selected 4B/v2 configuration had one false positive (`eval_083`): a "
            "genuine sign-in code that explicitly says not to share it. The output "
            "listed "
            "all ten tactics while providing no red flags. This is a schema-consistent "
            "but internally inconsistent response. A future prompt or post-validator "
            "should require each tactic to cite message-local evidence and reject a "
            "nonempty tactic list when `red_flags` is empty.",
            "",
            "The 8B configurations shared two false negatives (`eval_003`, "
            "`eval_002`), "
            "both package/redelivery smishing messages. They treated reserved-domain "
            "links and a small fee or short deadline as ordinary delivery logistics. "
            "A future training set should add varied low-fee delivery hard cases and "
            "explicitly teach that a link plus payment/address action can be evidence "
            "even when the amount and prose are plausible. Their common false positive "
            "was another genuine 2FA code (`eval_084`), indicating that 'never share' "
            "language is not consistently recognized as a legitimate safety signal.",
            "",
            "The 4B/v1 model's 13 errors were all false negatives, primarily subtle "
            "impersonation, relationship, delivery, and credential-request messages. "
            "The few-shot calibration in v2 eliminated those misses. Both 1.7B runs "
            "severely undercalled scams at the constrained threshold; v2 could not "
            "separate classes at any nonzero-recall threshold under 5% FPR.",
            "",
            "No prompt was changed after these results. TEST remained locked "
            "throughout.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render DEV experiment Markdown")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    report = json.loads(args.input.read_text(encoding="utf-8"))
    args.output.write_text(render_dev_report(report), encoding="utf-8")


if __name__ == "__main__":
    main()

# Phase 1 final held-out evaluation

Generated: 2026-10-17T23:31:22.962563+00:00
Data: `data/eval/test.csv` (60 locked TEST examples)

The configuration was frozen from DEV before this single audited TEST run. No thresholds, prompt text, examples, or calibration parameters were changed after TEST was viewed.

## Result

| Model | Precision | Recall | F1 | FPR | Accuracy | 95% recall CI | 95% FPR CI |
|---|---:|---:|---:|---:|---:|---:|---:|
| frozen_local_llm | 96.6% | 100.0% | 98.2% | 3.1% | 98.3% | 87.9%-100.0% | 0.6%-15.7% |
| always_scam | 46.7% | 100.0% | 63.6% | 100.0% | 46.7% | 87.9%-100.0% | 89.3%-100.0% |
| random_seed_0 | 45.7% | 57.1% | 50.8% | 59.4% | 48.3% | 39.1%-73.5% | 42.3%-74.5% |
| tfidf_logistic_regression | 60.0% | 21.4% | 31.6% | 12.5% | 56.7% | 10.2%-39.5% | 5.0%-28.1% |

The primary target (recall >= 90% at FPR <= 5%) was met. The preferred FPR <= 3% was not met: one false positive among 32 legitimate messages is 3.125%.

Frozen LLM confusion matrix: TN=31, FP=1, FN=0, TP=28. Structured-output errors: 0.

Median latency was 2.864s; P95 was 3.577s; mean generation throughput was 29.2 tok/s.

## Frozen identity

- Model: `qwen3:4b-instruct-2507-q4_K_M`
- Prompt: v2 / `a60ea14fb94faf1e86d221ea40db0d337889eaae9cca17a1511fc775ed7497d8`
- Dangerous threshold: 0.697270922355255
- Calibration: DEV-fitted Platt scaling, coefficient 4.528079812720718, intercept -2.108916117595825

## Frozen LLM per-category results

| Category | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| bank_alert | 3 | 100.0% | 100.0% | 0.0% |
| family_emergency | 3 | 100.0% | 100.0% | 0.0% |
| government_impersonation | 3 | 100.0% | 100.0% | 0.0% |
| investment_crypto | 3 | 100.0% | 100.0% | 0.0% |
| job_offer | 2 | 100.0% | 100.0% | 0.0% |
| marketplace | 2 | 100.0% | 100.0% | 0.0% |
| other | 34 | 66.7% | 100.0% | 3.1% |
| package_delivery | 2 | 100.0% | 100.0% | 0.0% |
| prize_or_lottery | 2 | 100.0% | 100.0% | 0.0% |
| romance | 2 | 100.0% | 100.0% | 0.0% |
| tech_support | 2 | 100.0% | 100.0% | 0.0% |
| utility_or_billing | 2 | 100.0% | 100.0% | 0.0% |

## Final error analysis

There were no false negatives. The single false positive was `eval_090`, a genuine sign-in approval code that tells the user to deny an unfamiliar request inside the app. As on DEV, the model returned all ten tactics but an empty red-flag list. This confirms the need for an evidence-consistency validator and more genuine 2FA hard negatives; it does not justify a post-TEST threshold change.

The 95% intervals are wide because TEST contains only 28 scams and 32 legitimate messages. The observed target pass should therefore be treated as promising, not production validation.

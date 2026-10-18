# Phase 1 DEV model experiments

Generated: 2026-10-17T23:24:38.177302+00:00
Data: `data/eval/dev.csv` (DEV only; TEST remained locked)

Platt scaling and all thresholds were fit on DEV. Confidence intervals are 95% Wilson intervals. These are model-selection results, not unbiased final generalization estimates.

## Comparison

| Model | Prompt | P | R | F1 | FPR | Errors | Median | P95 | tok/s |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `qwen3:1.7b-q4_K_M` | v1 | 66.7% | 4.8% | 8.9% | 2.1% | 0 | 3.36s | 3.98s | 28.9 |
| `qwen3:1.7b-q4_K_M` | v2 | 0.0% | 0.0% | 0.0% | 0.0% | 0 | 1.88s | 3.93s | 53.6 |
| `qwen3:4b-instruct-2507-q4_K_M` | v1 | 100.0% | 69.0% | 81.7% | 0.0% | 0 | 3.31s | 7.74s | 24.0 |
| `qwen3:4b-instruct-2507-q4_K_M` | v2 | 97.7% | 100.0% | 98.8% | 2.1% | 0 | 3.61s | 4.16s | 23.7 |
| `qwen3:8b-q4_K_M` | v1 | 97.6% | 95.2% | 96.4% | 2.1% | 0 | 8.64s | 11.65s | 13.2 |
| `qwen3:8b-q4_K_M` | v2 | 97.6% | 95.2% | 96.4% | 2.1% | 0 | 7.08s | 12.95s | 12.7 |

## Frozen selection for final evaluation

`qwen3:4b-instruct-2507-q4_K_M` with prompt v2 was selected because it maximized recall under the 5% FPR constraint. It returned 42/42 scam messages and flagged 1/48 legitimate messages on DEV. No third prompt iteration was performed.

Its frozen prompt SHA-256 and calibrated thresholds are recorded below and must not be changed after viewing TEST.

## qwen3:1.7b-q4_K_M / v1

Prompt SHA-256: `c9c1ffe646c94f0a043fa395411273e79b6a18c9e4deabfabfc048ffe321a1da`. Few-shot examples: 0 (none).
Valid responses: 90/90; explicit errors: 0.
Confusion matrix at the selected dangerous threshold: TN=47, FP=1, FN=40, TP=2.
Precision 66.7% (CI 20.8%-93.9%); recall 4.8% (CI 1.3%-15.8%); F1 8.9%; FPR 2.1% (CI 0.4%-10.9%).
Frozen mapping: safe below 0.564330; suspicious below 0.632422; dangerous at or above 0.632422.

### Reliability after DEV Platt scaling

| Score bin | Count | Mean score | Observed scam rate |
|---|---:|---:|---:|
| 0.0%-20.0% | 18 | 15.1% | 0.0% |
| 20.0%-40.0% | 0 | — | — |
| 40.0%-60.0% | 69 | 54.2% | 58.0% |
| 60.0%-80.0% | 3 | 63.2% | 66.7% |
| 80.0%-100.0% | 0 | — | — |

### Per-category

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| bank_alert | 3 | 0.0% | 0.0% | 0.0% |
| family_emergency | 3 | 0.0% | 0.0% | 0.0% |
| government_impersonation | 3 | 0.0% | 0.0% | 0.0% |
| investment_crypto | 3 | 0.0% | 0.0% | 0.0% |
| job_offer | 4 | 100.0% | 25.0% | 0.0% |
| marketplace | 4 | 0.0% | 0.0% | 0.0% |
| other | 52 | 0.0% | 0.0% | 2.1% |
| package_delivery | 4 | 0.0% | 0.0% | 0.0% |
| prize_or_lottery | 3 | 0.0% | 0.0% | 0.0% |
| romance | 3 | 0.0% | 0.0% | 0.0% |
| tech_support | 4 | 100.0% | 25.0% | 0.0% |
| utility_or_billing | 4 | 0.0% | 0.0% | 0.0% |

### Per-channel

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 17 | 100.0% | 11.1% | 0.0% |
| email | 27 | 50.0% | 9.1% | 6.2% |
| other | 9 | 0.0% | 0.0% | 0.0% |
| sms | 29 | 0.0% | 0.0% | 0.0% |
| social | 8 | 0.0% | 0.0% | 0.0% |

### Tactic extraction

| Tactic | Support | Precision | Recall |
|---|---:|---:|---:|
| urgency | 39 | 35.0% | 17.9% |
| threat | 11 | 33.3% | 18.2% |
| impersonation | 25 | 30.8% | 32.0% |
| unusual_payment | 27 | 100.0% | 14.8% |
| credential_request | 11 | 66.7% | 18.2% |
| off_platform_push | 7 | 28.6% | 28.6% |
| too_good_to_be_true | 10 | 100.0% | 30.0% |
| secrecy | 6 | 0.0% | 0.0% |
| lookalike_link | 11 | 100.0% | 27.3% |
| relationship_exploit | 6 | 75.0% | 50.0% |

### Errors

False positives: eval_074.
False negatives: eval_058, eval_068, eval_035, eval_040, eval_042, eval_026, eval_055, eval_060, eval_056, eval_034, eval_010, eval_006, eval_003, eval_046, eval_067, eval_027, eval_049, eval_051, eval_038, eval_016, eval_020, eval_057, eval_017, eval_011, eval_029, eval_024, eval_041, eval_012, eval_061, eval_064, eval_033, eval_015, eval_069, eval_045, eval_004, eval_019, eval_052, eval_066, eval_002, eval_062.

## qwen3:1.7b-q4_K_M / v2

Prompt SHA-256: `a60ea14fb94faf1e86d221ea40db0d337889eaae9cca17a1511fc775ed7497d8`. Few-shot examples: 6 (pool_0019, pool_0073, pool_0145, pool_0217, pool_0289, pool_0361).
Valid responses: 90/90; explicit errors: 0.
Confusion matrix at the selected dangerous threshold: TN=48, FP=0, FN=42, TP=0.
Precision 0.0% (CI 0.0%-0.0%); recall 0.0% (CI 0.0%-8.4%); F1 0.0%; FPR 0.0% (CI 0.0%-7.4%).
Frozen mapping: safe below 0.640044; suspicious below 1.000000; dangerous at or above 1.000000.

### Reliability after DEV Platt scaling

| Score bin | Count | Mean score | Observed scam rate |
|---|---:|---:|---:|
| 0.0%-20.0% | 37 | 13.9% | 5.4% |
| 20.0%-40.0% | 0 | — | — |
| 40.0%-60.0% | 0 | — | — |
| 60.0%-80.0% | 53 | 69.5% | 75.5% |
| 80.0%-100.0% | 0 | — | — |

### Per-category

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| bank_alert | 3 | 0.0% | 0.0% | 0.0% |
| family_emergency | 3 | 0.0% | 0.0% | 0.0% |
| government_impersonation | 3 | 0.0% | 0.0% | 0.0% |
| investment_crypto | 3 | 0.0% | 0.0% | 0.0% |
| job_offer | 4 | 0.0% | 0.0% | 0.0% |
| marketplace | 4 | 0.0% | 0.0% | 0.0% |
| other | 52 | 0.0% | 0.0% | 0.0% |
| package_delivery | 4 | 0.0% | 0.0% | 0.0% |
| prize_or_lottery | 3 | 0.0% | 0.0% | 0.0% |
| romance | 3 | 0.0% | 0.0% | 0.0% |
| tech_support | 4 | 0.0% | 0.0% | 0.0% |
| utility_or_billing | 4 | 0.0% | 0.0% | 0.0% |

### Per-channel

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 17 | 0.0% | 0.0% | 0.0% |
| email | 27 | 0.0% | 0.0% | 0.0% |
| other | 9 | 0.0% | 0.0% | 0.0% |
| sms | 29 | 0.0% | 0.0% | 0.0% |
| social | 8 | 0.0% | 0.0% | 0.0% |

### Tactic extraction

| Tactic | Support | Precision | Recall |
|---|---:|---:|---:|
| urgency | 39 | 70.6% | 61.5% |
| threat | 11 | 28.6% | 18.2% |
| impersonation | 25 | 88.9% | 32.0% |
| unusual_payment | 27 | 100.0% | 40.7% |
| credential_request | 11 | 70.0% | 63.6% |
| off_platform_push | 7 | 85.7% | 85.7% |
| too_good_to_be_true | 10 | 100.0% | 70.0% |
| secrecy | 6 | 41.7% | 83.3% |
| lookalike_link | 11 | 75.0% | 81.8% |
| relationship_exploit | 6 | 66.7% | 100.0% |

### Errors

False positives: none.
False negatives: eval_058, eval_068, eval_035, eval_040, eval_042, eval_026, eval_055, eval_060, eval_056, eval_034, eval_010, eval_006, eval_003, eval_046, eval_067, eval_027, eval_049, eval_051, eval_038, eval_016, eval_020, eval_057, eval_036, eval_017, eval_011, eval_029, eval_024, eval_041, eval_012, eval_061, eval_064, eval_033, eval_023, eval_015, eval_069, eval_045, eval_004, eval_019, eval_052, eval_066, eval_002, eval_062.

## qwen3:4b-instruct-2507-q4_K_M / v1

Prompt SHA-256: `c9c1ffe646c94f0a043fa395411273e79b6a18c9e4deabfabfc048ffe321a1da`. Few-shot examples: 0 (none).
Valid responses: 90/90; explicit errors: 0.
Confusion matrix at the selected dangerous threshold: TN=48, FP=0, FN=13, TP=29.
Precision 100.0% (CI 88.3%-100.0%); recall 69.0% (CI 54.0%-80.9%); F1 81.7%; FPR 0.0% (CI 0.0%-7.4%).
Frozen mapping: safe below 0.731959; suspicious below 0.808454; dangerous at or above 0.808454.

### Reliability after DEV Platt scaling

| Score bin | Count | Mean score | Observed scam rate |
|---|---:|---:|---:|
| 0.0%-20.0% | 44 | 12.2% | 0.0% |
| 20.0%-40.0% | 0 | — | — |
| 40.0%-60.0% | 0 | — | — |
| 60.0%-80.0% | 17 | 72.6% | 76.5% |
| 80.0%-100.0% | 29 | 83.8% | 100.0% |

### Per-category

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| bank_alert | 3 | 100.0% | 66.7% | 0.0% |
| family_emergency | 3 | 100.0% | 100.0% | 0.0% |
| government_impersonation | 3 | 100.0% | 100.0% | 0.0% |
| investment_crypto | 3 | 100.0% | 100.0% | 0.0% |
| job_offer | 4 | 100.0% | 75.0% | 0.0% |
| marketplace | 4 | 100.0% | 75.0% | 0.0% |
| other | 52 | 100.0% | 50.0% | 0.0% |
| package_delivery | 4 | 0.0% | 0.0% | 0.0% |
| prize_or_lottery | 3 | 100.0% | 100.0% | 0.0% |
| romance | 3 | 100.0% | 33.3% | 0.0% |
| tech_support | 4 | 100.0% | 100.0% | 0.0% |
| utility_or_billing | 4 | 100.0% | 50.0% | 0.0% |

### Per-channel

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 17 | 100.0% | 66.7% | 0.0% |
| email | 27 | 100.0% | 81.8% | 0.0% |
| other | 9 | 100.0% | 80.0% | 0.0% |
| sms | 29 | 100.0% | 70.0% | 0.0% |
| social | 8 | 100.0% | 42.9% | 0.0% |

### Tactic extraction

| Tactic | Support | Precision | Recall |
|---|---:|---:|---:|
| urgency | 39 | 67.6% | 64.1% |
| threat | 11 | 21.4% | 54.5% |
| impersonation | 25 | 54.3% | 76.0% |
| unusual_payment | 27 | 71.4% | 92.6% |
| credential_request | 11 | 31.2% | 90.9% |
| off_platform_push | 7 | 17.1% | 100.0% |
| too_good_to_be_true | 10 | 32.3% | 100.0% |
| secrecy | 6 | 15.8% | 100.0% |
| lookalike_link | 11 | 28.2% | 100.0% |
| relationship_exploit | 6 | 14.3% | 83.3% |

### Errors

False positives: none.
False negatives: eval_068, eval_026, eval_055, eval_060, eval_006, eval_003, eval_029, eval_041, eval_012, eval_064, eval_069, eval_004, eval_002.

## qwen3:4b-instruct-2507-q4_K_M / v2

Prompt SHA-256: `a60ea14fb94faf1e86d221ea40db0d337889eaae9cca17a1511fc775ed7497d8`. Few-shot examples: 6 (pool_0019, pool_0073, pool_0145, pool_0217, pool_0289, pool_0361).
Valid responses: 90/90; explicit errors: 0.
Confusion matrix at the selected dangerous threshold: TN=47, FP=1, FN=0, TP=42.
Precision 97.7% (CI 87.9%-99.6%); recall 100.0% (CI 91.6%-100.0%); F1 98.8%; FPR 2.1% (CI 0.4%-10.9%).
Frozen mapping: safe below 0.482187; suspicious below 0.697271; dangerous at or above 0.697271.

### Reliability after DEV Platt scaling

| Score bin | Count | Mean score | Observed scam rate |
|---|---:|---:|---:|
| 0.0%-20.0% | 45 | 13.2% | 0.0% |
| 20.0%-40.0% | 0 | — | — |
| 40.0%-60.0% | 2 | 48.2% | 0.0% |
| 60.0%-80.0% | 18 | 70.0% | 94.4% |
| 80.0%-100.0% | 25 | 90.0% | 100.0% |

### Per-category

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| bank_alert | 3 | 100.0% | 100.0% | 0.0% |
| family_emergency | 3 | 100.0% | 100.0% | 0.0% |
| government_impersonation | 3 | 100.0% | 100.0% | 0.0% |
| investment_crypto | 3 | 100.0% | 100.0% | 0.0% |
| job_offer | 4 | 100.0% | 100.0% | 0.0% |
| marketplace | 4 | 100.0% | 100.0% | 0.0% |
| other | 52 | 80.0% | 100.0% | 2.1% |
| package_delivery | 4 | 100.0% | 100.0% | 0.0% |
| prize_or_lottery | 3 | 100.0% | 100.0% | 0.0% |
| romance | 3 | 100.0% | 100.0% | 0.0% |
| tech_support | 4 | 100.0% | 100.0% | 0.0% |
| utility_or_billing | 4 | 100.0% | 100.0% | 0.0% |

### Per-channel

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 17 | 100.0% | 100.0% | 0.0% |
| email | 27 | 100.0% | 100.0% | 0.0% |
| other | 9 | 100.0% | 100.0% | 0.0% |
| sms | 29 | 90.9% | 100.0% | 5.3% |
| social | 8 | 100.0% | 100.0% | 0.0% |

### Tactic extraction

| Tactic | Support | Precision | Recall |
|---|---:|---:|---:|
| urgency | 39 | 68.4% | 100.0% |
| threat | 11 | 25.0% | 100.0% |
| impersonation | 25 | 50.0% | 100.0% |
| unusual_payment | 27 | 56.2% | 100.0% |
| credential_request | 11 | 22.4% | 100.0% |
| off_platform_push | 7 | 13.7% | 100.0% |
| too_good_to_be_true | 10 | 21.3% | 100.0% |
| secrecy | 6 | 10.9% | 100.0% |
| lookalike_link | 11 | 22.0% | 100.0% |
| relationship_exploit | 6 | 12.0% | 100.0% |

### Errors

False positives: eval_083.
False negatives: none.

## qwen3:8b-q4_K_M / v1

Prompt SHA-256: `c9c1ffe646c94f0a043fa395411273e79b6a18c9e4deabfabfc048ffe321a1da`. Few-shot examples: 0 (none).
Valid responses: 90/90; explicit errors: 0.
Confusion matrix at the selected dangerous threshold: TN=47, FP=1, FN=2, TP=40.
Precision 97.6% (CI 87.4%-99.6%); recall 95.2% (CI 84.2%-98.7%); F1 96.4%; FPR 2.1% (CI 0.4%-10.9%).
Frozen mapping: safe below 0.639765; suspicious below 0.728280; dangerous at or above 0.728280.

### Reliability after DEV Platt scaling

| Score bin | Count | Mean score | Observed scam rate |
|---|---:|---:|---:|
| 0.0%-20.0% | 48 | 13.5% | 4.2% |
| 20.0%-40.0% | 0 | — | — |
| 40.0%-60.0% | 0 | — | — |
| 60.0%-80.0% | 7 | 71.6% | 71.4% |
| 80.0%-100.0% | 35 | 87.1% | 100.0% |

### Per-category

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| bank_alert | 3 | 100.0% | 100.0% | 0.0% |
| family_emergency | 3 | 100.0% | 100.0% | 0.0% |
| government_impersonation | 3 | 100.0% | 100.0% | 0.0% |
| investment_crypto | 3 | 100.0% | 100.0% | 0.0% |
| job_offer | 4 | 100.0% | 100.0% | 0.0% |
| marketplace | 4 | 100.0% | 100.0% | 0.0% |
| other | 52 | 80.0% | 100.0% | 2.1% |
| package_delivery | 4 | 100.0% | 50.0% | 0.0% |
| prize_or_lottery | 3 | 100.0% | 100.0% | 0.0% |
| romance | 3 | 100.0% | 100.0% | 0.0% |
| tech_support | 4 | 100.0% | 100.0% | 0.0% |
| utility_or_billing | 4 | 100.0% | 100.0% | 0.0% |

### Per-channel

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 17 | 100.0% | 88.9% | 0.0% |
| email | 27 | 90.9% | 90.9% | 6.2% |
| other | 9 | 100.0% | 100.0% | 0.0% |
| sms | 29 | 100.0% | 100.0% | 0.0% |
| social | 8 | 100.0% | 100.0% | 0.0% |

### Tactic extraction

| Tactic | Support | Precision | Recall |
|---|---:|---:|---:|
| urgency | 39 | 100.0% | 15.4% |
| threat | 11 | 40.0% | 18.2% |
| impersonation | 25 | 83.3% | 20.0% |
| unusual_payment | 27 | 100.0% | 77.8% |
| credential_request | 11 | 63.6% | 63.6% |
| off_platform_push | 7 | 100.0% | 85.7% |
| too_good_to_be_true | 10 | 100.0% | 30.0% |
| secrecy | 6 | 100.0% | 66.7% |
| lookalike_link | 11 | 100.0% | 72.7% |
| relationship_exploit | 6 | 100.0% | 66.7% |

### Errors

False positives: eval_084.
False negatives: eval_003, eval_002.

## qwen3:8b-q4_K_M / v2

Prompt SHA-256: `a60ea14fb94faf1e86d221ea40db0d337889eaae9cca17a1511fc775ed7497d8`. Few-shot examples: 6 (pool_0019, pool_0073, pool_0145, pool_0217, pool_0289, pool_0361).
Valid responses: 90/90; explicit errors: 0.
Confusion matrix at the selected dangerous threshold: TN=47, FP=1, FN=2, TP=40.
Precision 97.6% (CI 87.4%-99.6%); recall 95.2% (CI 84.2%-98.7%); F1 96.4%; FPR 2.1% (CI 0.4%-10.9%).
Frozen mapping: safe below 0.000000; suspicious below 0.744180; dangerous at or above 0.744180.

### Reliability after DEV Platt scaling

| Score bin | Count | Mean score | Observed scam rate |
|---|---:|---:|---:|
| 0.0%-20.0% | 49 | 13.4% | 4.1% |
| 20.0%-40.0% | 0 | — | — |
| 40.0%-60.0% | 0 | — | — |
| 60.0%-80.0% | 2 | 74.4% | 50.0% |
| 80.0%-100.0% | 39 | 87.1% | 100.0% |

### Per-category

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| bank_alert | 3 | 100.0% | 100.0% | 0.0% |
| family_emergency | 3 | 100.0% | 100.0% | 0.0% |
| government_impersonation | 3 | 100.0% | 100.0% | 0.0% |
| investment_crypto | 3 | 100.0% | 100.0% | 0.0% |
| job_offer | 4 | 100.0% | 100.0% | 0.0% |
| marketplace | 4 | 100.0% | 100.0% | 0.0% |
| other | 52 | 80.0% | 100.0% | 2.1% |
| package_delivery | 4 | 100.0% | 50.0% | 0.0% |
| prize_or_lottery | 3 | 100.0% | 100.0% | 0.0% |
| romance | 3 | 100.0% | 100.0% | 0.0% |
| tech_support | 4 | 100.0% | 100.0% | 0.0% |
| utility_or_billing | 4 | 100.0% | 100.0% | 0.0% |

### Per-channel

| Group | N | Precision | Recall | FPR |
|---|---:|---:|---:|---:|
| chat | 17 | 100.0% | 88.9% | 0.0% |
| email | 27 | 90.9% | 90.9% | 6.2% |
| other | 9 | 100.0% | 100.0% | 0.0% |
| sms | 29 | 100.0% | 100.0% | 0.0% |
| social | 8 | 100.0% | 100.0% | 0.0% |

### Tactic extraction

| Tactic | Support | Precision | Recall |
|---|---:|---:|---:|
| urgency | 39 | 100.0% | 41.0% |
| threat | 11 | 66.7% | 18.2% |
| impersonation | 25 | 91.7% | 44.0% |
| unusual_payment | 27 | 100.0% | 88.9% |
| credential_request | 11 | 70.0% | 63.6% |
| off_platform_push | 7 | 100.0% | 100.0% |
| too_good_to_be_true | 10 | 85.7% | 60.0% |
| secrecy | 6 | 85.7% | 100.0% |
| lookalike_link | 11 | 100.0% | 72.7% |
| relationship_exploit | 6 | 100.0% | 83.3% |

### Errors

False positives: eval_084.
False negatives: eval_003, eval_002.

## Written error analysis

The selected 4B/v2 configuration had one false positive (`eval_083`): a genuine sign-in code that explicitly says not to share it. The output listed all ten tactics while providing no red flags. This is a schema-consistent but internally inconsistent response. A future prompt or post-validator should require each tactic to cite message-local evidence and reject a nonempty tactic list when `red_flags` is empty.

The 8B configurations shared two false negatives (`eval_003`, `eval_002`), both package/redelivery smishing messages. They treated reserved-domain links and a small fee or short deadline as ordinary delivery logistics. A future training set should add varied low-fee delivery hard cases and explicitly teach that a link plus payment/address action can be evidence even when the amount and prose are plausible. Their common false positive was another genuine 2FA code (`eval_084`), indicating that 'never share' language is not consistently recognized as a legitimate safety signal.

The 4B/v1 model's 13 errors were all false negatives, primarily subtle impersonation, relationship, delivery, and credential-request messages. The few-shot calibration in v2 eliminated those misses. Both 1.7B runs severely undercalled scams at the constrained threshold; v2 could not separate classes at any nonzero-recall threshold under 5% FPR.

No prompt was changed after these results. TEST remained locked throughout.

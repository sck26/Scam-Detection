# Phase 1: detection engine report

Completed 2026-10-17. All inference stayed on this machine through Ollama's
loopback interface; no message data was sent to a hosted model or external API.
Every result below comes from the committed JSON run artifacts.

## Hardware and candidates

Benchmarks ran on macOS 26.6.2, an Apple M4 MacBook Air with 10 CPU cores,
8 GPU cores, 16 GB unified memory, and approximately 15 GiB free disk at model
selection time. Ollama 0.34.4 used Metal and reported 11.8 GiB available to its
local runtime.

The official Ollama library was checked on 2026-10-17. All candidates used
Q4_K_M quantization and Apache-2.0 licensing:

| Role | Exact tag | Parameters | Download |
|---|---|---:|---:|
| Small | `qwen3:1.7b-q4_K_M` | 1.7B | 1.4 GB |
| Small | `qwen3:4b-instruct-2507-q4_K_M` | 4B | 2.5 GB |
| Mid | `qwen3:8b-q4_K_M` | 8.19B | 5.2 GB |

A 14B Q4 candidate was not comfortable on this machine: its 9.3 GB artifact
would have exceeded the observed free disk when added to the 9.1 GB selected set
and left little unified memory for context and the OS. Exact source links and
installation instructions are in `docs/phase1/MODELS.md`.

## DEV experiments

DEV contains 90 messages (42 scam, 48 legitimate). Each of three models was run
with prompt v1 (zero-shot) and v2 (six pool-only few-shot examples), for 540 real
inferences. Hidden thinking was disabled; JSON was schema-constrained and
validated. All six combinations returned 90/90 valid responses with zero parse
errors. Platt scaling and thresholds were fit on DEV only; intervals are Wilson
95% intervals.

| Model | Prompt | Precision | Recall | F1 | FPR | Median | P95 | tok/s |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen3 1.7B | v1 | 66.7% | 4.8% | 8.9% | 2.1% | 3.36s | 3.98s | 28.9 |
| Qwen3 1.7B | v2 | 0.0% | 0.0% | 0.0% | 0.0% | 1.88s | 3.93s | 53.6 |
| Qwen3 4B Instruct | v1 | 100.0% | 69.0% | 81.7% | 0.0% | 3.31s | 7.74s | 24.0 |
| Qwen3 4B Instruct | v2 | 97.7% | 100.0% | 98.8% | 2.1% | 3.61s | 4.16s | 23.7 |
| Qwen3 8B | v1 | 97.6% | 95.2% | 96.4% | 2.1% | 8.64s | 11.65s | 13.2 |
| Qwen3 8B | v2 | 97.6% | 95.2% | 96.4% | 2.1% | 7.08s | 12.95s | 12.7 |

The 4B/v2 configuration maximized recall under the 5% FPR constraint and was
frozen before TEST. Its prompt SHA-256 is
`a60ea14fb94faf1e86d221ea40db0d337889eaae9cca17a1511fc775ed7497d8`.
The DEV-fitted Platt coefficient is 4.528079812720718 and intercept is
-2.1089161175958253. The frozen dangerous threshold is
0.6972709223552555 and safe threshold is 0.4821874908096537.

The complete reliability tables, per-category/per-channel results, tactic
precision/recall, Wilson intervals, and every error ID are in
`docs/phase1/results/dev_results.md` and its JSON source.

### DEV error analysis

The selected configuration's sole error was a false positive on `eval_083`, a
genuine 2FA code saying not to share it. It returned all ten tactics but no red
flags—valid JSON, but internally inconsistent evidence. The 8B variants missed
two low-friction package/redelivery scams and also false-positived a genuine 2FA
message. The 4B/v1 model had 13 false negatives across subtle impersonation,
relationship, delivery, and credential requests. The six pool examples in v2
eliminated those misses. No third prompt iteration was made.

Priorities from these errors are an evidence-consistency validator, tactic-to-
span grounding, more genuine 2FA hard negatives, and varied low-fee delivery
scams. None was applied after viewing TEST.

## Single held-out TEST evaluation

The locked 60-row TEST set (28 scam, 32 legitimate) was scored once by the
frozen LLM configuration. The same invocation evaluated all baselines. The local
audit log contains one STARTED/COMPLETED pair.

| Model | Precision | Recall | F1 | FPR | Accuracy | Recall 95% CI | FPR 95% CI |
|---|---:|---:|---:|---:|---:|---:|---:|
| Frozen 4B/v2 LLM | 96.6% | 100.0% | 98.2% | 3.1% | 98.3% | 87.9%-100.0% | 0.6%-15.7% |
| Always scam | 46.7% | 100.0% | 63.6% | 100.0% | 46.7% | 87.9%-100.0% | 89.3%-100.0% |
| Random seed 0 | 45.7% | 57.1% | 50.8% | 59.4% | 48.3% | 39.1%-73.5% | 42.3%-74.5% |
| TF-IDF logistic | 60.0% | 21.4% | 31.6% | 12.5% | 56.7% | 10.2%-39.5% | 5.0%-28.1% |

The primary target—recall at least 90% with FPR at most 5%—was met: TN=31,
FP=1, FN=0, TP=28. The preferred FPR at most 3% was narrowly missed; 1/32 is
3.125%. There were zero structured-output errors. Median LLM latency was 2.864s,
P95 was 3.577s, and generation averaged 29.2 tokens/s.

The single TEST false positive, `eval_090`, was another genuine sign-in approval
code. It reproduced the all-tactics/no-red-flags inconsistency seen on DEV. The
threshold was not changed. Full per-category numbers and frozen identity are in
`docs/phase1/results/final_results.md` and JSON.

## Distilled on-device student

The teacher labeled a leakage-checked, balanced set of 600 non-eval messages:
all 432 pool rows plus 168 deterministic UCI samples. It agreed with original
labels on 97.17%. Confidence filtering kept 593 and dropped 7; 474 trained the
student and 119 formed its threshold-calibration split.

The student is word TF-IDF (1–2 grams, 1,650 features) plus logistic regression.
On DEV at its pool-calibrated dangerous threshold it achieved 100.0% precision,
54.8% recall, 70.8% F1, and 0.0% FPR (TN=48, FP=0, FN=19, TP=23). Its decisions
agreed with the teacher on 77.8% of DEV. With safe/dangerous thresholds of
0.6300619475935576/0.670274239493989, it resolved 86.7% of DEV without escalation
at 91.0% accuracy; uncertain messages escalate to the LLM. Measured batch latency
was 0.010 ms per DEV message on this Mac.

The complete ONNX text pipeline is 62,995 bytes and passed a runtime smoke test.
The joblib source is 78,897 bytes. No quantization was used; float32 is already
small. Direct Core ML conversion failed because coremltools does not support
`TfidfVectorizer`. A 6,767-byte Core ML linear head, 89,654-byte preprocessing
manifest, and exact iOS integration steps are committed under
`artifacts/student/`; a native macOS smoke inference returned probability
0.5611003 for a zero vector.

The student was not scored on TEST after Step 6. Doing so would have violated the
single held-out-run rule. This is an explicit acceptance shortfall, chosen to
preserve evaluation integrity rather than invent or obtain a second TEST result.
Multi-label tactic heads were also not feasible for this small linear student.

## Known limitations

- DEV/TEST are small, synthetic, English-only sets; confidence intervals are wide.
- Synthetic identifiers and domains do not represent every production domain.
- The UCI corpus is old SMS spam; only 168 balanced rows were teacher-labeled.
- No live URL reputation, redirect inspection, sender authentication, image/OCR,
  attachment, conversation-history, or multilingual analysis exists yet.
- Scores are calibrated on a small DEV split and may drift by channel/population.
- LLM latency is too high for an always-on mobile first pass.
- The Core ML artifact requires app-side TF-IDF preprocessing.
- No iOS app, backend, privacy review, or adversarial/red-team evaluation exists.

## Prioritized next improvements

1. Add tactic-to-text evidence constraints and reject inconsistent outputs.
2. Expand genuinely sourced, consented multilingual evaluation with realistic
   prevalence; retain a new untouched release-gate split.
3. Add more legitimate 2FA/bank/delivery hard negatives and subtle modern scams.
4. Train a compact transformer student with binary and tactic heads, then convert
   the full tokenizer/model to Core ML and benchmark on target iPhones.
5. Add URL parsing/reputation and sender/authentication signals behind explicit
   privacy and retention boundaries.
6. Validate calibration and escalation thresholds prospectively by channel.

## Manual/external workarounds

Only UCI SMS was locally available. SpearPhishMX still requires the manual
Mendeley download documented in `data/README.md`. URLhaus and PhishTank require
local API keys; OpenPhish requires explicit terms review and may be unsuitable
for commercial use. None was invented or silently substituted. Model weights,
public raw data, caches, checkpoints, audit logs, and teacher labels remain
uncommitted.

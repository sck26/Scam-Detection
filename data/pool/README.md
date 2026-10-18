# Development and distillation pool

`pool.csv` contains 432 original synthetic messages: 216 scam and 216 legitimate. It is balanced across all 12 scam reporting categories; channels rotate across SMS, email, chat, social, and other; all taxonomy tactics are represented. Every legitimate row is a deliberate hard negative. Identifiers and links are reserved or fictional.

This pool may be used for few-shot selection, prompt development, calibration experiments, and teacher/student distillation. It is never evaluation data. Do not calculate product metrics on it or move its rows into DEV or TEST.

Before adding or changing examples, run `make leakage` and `make test`. No ID, normalized exact text, or near-duplicate at the configured similarity threshold may cross between this pool and any evaluation set.


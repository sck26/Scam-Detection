# Phase 0 completion report

Verified from an isolated clean clone on 2026-10-16 with Python 3.12 (the
project supports Python 3.11+).

## Built

- Monorepo placeholders for iOS, backend, infrastructure, data, documentation,
  reports, and CI.
- Reproducible Python package/tooling with `uv` support and a venv/pip fallback.
- Typed, duplicate-key-safe shared danger/channel/tactic/category taxonomy.
- Source-documented public-data pipeline and unified processed schema.
- A committed 150-row original synthetic evaluation set: 70 scam examples and
  80 legitimate hard negatives, covering every category and channel.
- Pluggable detector interface, binary/tactic metrics, threshold sweep,
  per-category/per-channel reporting, misclassification lists, and timestamped
  plus `latest` JSON/Markdown output.
- Always-scam, deterministic-random, and TF-IDF/logistic reference detectors.
- GitHub Actions workflow that runs lint, strict type checking, and offline
  fixture-backed tests without contacting dataset sources.
- Apple/account/entitlement checklist and planned system architecture.

## Clean-clone verification

The following commands passed in a separate clone:

```text
make setup
make lint
make typecheck
make test       # 13 passed
make eval
```

`make eval` downloaded and verified the official UCI archive (5,574 rows),
trained the TF-IDF/logistic detector only on normalized public data, evaluated
all three baselines on the committed set, and wrote timestamped and `latest`
JSON/Markdown reports. Generated data and reports remained ignored by Git.

## Baseline results at threshold 0.5

| Model | Precision | Recall | F1 | False-positive rate | Accuracy |
|---|---:|---:|---:|---:|---:|
| Always scam | 46.7% | 100.0% | 63.6% | 100.0% | 46.7% |
| Random (seed 0) | 48.8% | 60.0% | 53.8% | 55.0% | 52.0% |
| TF-IDF + logistic regression | 65.5% | 27.1% | 38.4% | 12.5% | 59.3% |

These are measuring-stick baselines, not product-quality claims. In particular,
the TF-IDF baseline's 12.5% false-positive rate and 72.9% false-negative rate
show why tactic modeling and threshold work are required in later phases.

## External/manual items not completed

- **SpearPhishMX email data:** the open CC BY 4.0 record uses an interactive
  Mendeley download and does not publish a stable direct file URL used here.
  Download `SpearPhishMX_dataset_publico.csv` from
  <https://data.mendeley.com/datasets/h4bxjk84jb/1>, place it at
  `data/raw/email/SpearPhishMX_dataset_publico.csv`, and run `make data`.
- **URLhaus:** current community exports require an abuse.ch Auth-Key. Create
  one at <https://auth.abuse.ch/>, set `URLHAUS_AUTH_KEY` in an untracked local
  `.env`/shell environment, and run `make data`.
- **OpenPhish:** the community feed's current terms restrict it to eligible
  non-commercial research and prohibit product/business use without written
  permission. Review <https://openphish.com/terms.html>; only if eligible, set
  `SCAMGUARD_ACCEPT_OPENPHISH_TERMS=1` locally and run `make data`. Obtain written
  commercial permission before any product use.
- **PhishTank (optional):** register an app key, set `PHISHTANK_API_KEY` locally,
  and run `make data`.
- **Hosted CI:** the workflow's exact commands pass locally, but GitHub Actions
  cannot run until a GitHub remote exists and these commits are pushed. Push the
  repository and confirm the first `CI` run is green.
- **Accounts/entitlements:** complete every applicable item in
  `docs/ACCOUNTS_AND_ENTITLEMENTS.md`, beginning with Apple enrollment and the
  Live Caller ID Lookup endpoint-validation request. Keep credentials in the
  named secret stores, never Git.
- **Repository license:** replace the placeholder `LICENSE` with a license
  approved by the repository owner/legal counsel before distribution.
- **Application/infrastructure:** create the Xcode project manually in a later
  phase; choose the cloud provider before provisioning. Phase 0 intentionally
  created no app, backend, detector service, or cloud resources.


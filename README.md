# ScamGuard

ScamGuard is an iOS-first scam-protection product. This repository contains the
Phase 0 foundations and the Phase 1 local detection engine: shared definitions,
reproducible data preparation, a locked evaluation workflow, local LLM adapters,
and a compact on-device student. It intentionally does not contain an application,
backend, or production service yet.

## Repository layout

- `ios/` — placeholder for the future Xcode project.
- `backend/` — placeholder for the future stateless API and workers.
- `ml/` — Python package, local detectors, tests, data preparation, and evaluation.
- `infra/` — placeholder for future Terraform; nothing is provisioned here.
- `data/` — source documentation and committed evaluation data. Downloaded raw
  and processed data are local-only.
- `docs/` — architecture and operational documentation.
- `artifacts/student/` — committed compact ONNX/Core ML student artifacts.
- `reports/` — generated caches, checkpoints, and audit logs (local-only).
- `.github/workflows/` — continuous integration.

## Getting started

Python 3.11 or newer is required. Ollama is optional for normal development and
CI; it is needed only to reproduce LLM experiments.

```bash
make setup
make lint
make typecheck
make test
make eval       # DEV baselines; downloads the documented UCI corpus
```

Useful local-only commands include `make hardware`, `make models`, `make
experiments`, and `python -m scamguard.detect "message" --model <tag>`. The
single held-out result is already committed; do not rerun `make final-eval` when
changing the detector. See `docs/PHASE1_REPORT.md` for results and limitations.

Never commit secrets, raw third-party data, downloaded model weights, teacher
label files, caches, or user messages.

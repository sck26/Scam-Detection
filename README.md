# ScamGuard

ScamGuard is an iOS-first scam-protection product. This repository contains the
Phase 0 foundations: shared definitions, reproducible data preparation, and an
evaluation harness. It intentionally does not contain an application, backend,
or production detector yet.

## Repository layout

- `ios/` — placeholder for the future Xcode project.
- `backend/` — placeholder for the future stateless API and workers.
- `ml/` — Python package, tests, data preparation, and evaluation tooling.
- `infra/` — placeholder for future Terraform; nothing is provisioned here.
- `data/` — source documentation and committed evaluation data. Downloaded raw
  and processed data are local-only.
- `docs/` — architecture and operational documentation.
- `reports/` — generated evaluation reports (local-only).
- `.github/workflows/` — continuous integration.

## Getting started

Python 3.11 or newer is required. Tooling and runnable commands are introduced
in the Phase 0 setup commits; see the `Makefile` once available. Never commit
secrets, raw third-party data, or generated reports.


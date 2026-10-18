# Hand-labeled evaluation set

`test_set.csv` is the committed, stable measuring stick for Phase 0. It has 150 original synthetic messages: 70 scams and 80 legitimate messages. No row was copied from a real message or public corpus, and no row contains real personal data. URLs use reserved `example.com`, `example.org`, or `example.net` domains; phone numbers use the fictional 555-01xx range.

Phase 1 keeps `test_set.csv` unchanged and deterministically partitions it with
seed `20261017` into `dev.csv` (90 rows) and locked `test.csv` (60 rows). DEV is
available for design and threshold work. The held-out TEST file can be scored
only with `--final`; each attempt appends an audit entry to the ignored local
`reports/test_runs.log` file. Do not inspect TEST errors while iterating.

## Schema

- `id`: unique stable identifier.
- `text`: message presented to a detector.
- `label`: `scam` or `legit`.
- `scam_category`: reporting category from the shared taxonomy. Legitimate rows use `other`.
- `channel`: channel from the shared taxonomy.
- `tactics`: pipe-separated tactic names from the shared taxonomy; empty for legitimate rows.
- `has_url`: lowercase `true` or `false`.
- `source`: always `synthetic` for this set.
- `notes`: provenance or the hard-negative role of the row.

## Adding examples

Write new examples from scratch; never paste a real user's message. Use only reserved domains and 555-01xx phone numbers. Assign tactics based on observable language rather than the scam category, leave tactics empty for legitimate examples, and run `make test`. Preserve existing IDs so reports remain comparable across revisions. Add difficult legitimate examples intentionally, because a low false-positive rate is a primary product requirement.

Pool examples live separately in `data/pool/`. Run `make leakage` before every
dataset commit. Pool rows may never be copied, paraphrased closely, or moved into
DEV or TEST.

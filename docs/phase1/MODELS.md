# Phase 1 local model candidates

Verified against the official Ollama library on 2026-10-17. The exact, immutable
configuration is in `ml/src/scamguard/models.yaml`.

## Benchmark machine

- macOS 26.6.2 on Apple silicon
- Apple M4: 10 CPU cores (4 performance, 6 efficiency), 8 GPU cores
- 16 GB unified memory
- 15 GiB free on the data volume at selection time
- Ollama client 0.34.4 was installed; no server was running during inspection

Serial number, hardware UUID, and similar device identifiers are deliberately excluded.
Run `make hardware` for a fresh, privacy-safe JSON inventory.

## Selected candidates

| Role | Exact Ollama tag | Parameters | Download | Quantization | License |
|---|---|---:|---:|---|---|
| Small | `qwen3:1.7b-q4_K_M` | 1.7B | 1.4 GB | Q4_K_M | Apache-2.0 |
| Small | `qwen3:4b-instruct-2507-q4_K_M` | 4B | 2.5 GB | Q4_K_M | Apache-2.0 |
| Mid-size | `qwen3:8b-q4_K_M` | 8.19B | 5.2 GB | Q4_K_M | Apache-2.0 |

The tags, artifact sizes, quantization, and licenses were checked on the official
[Qwen3 tag list](https://ollama.com/library/qwen3/tags) and the individual
[1.7B](https://ollama.com/library/qwen3:1.7b-q4_K_M),
[4B Instruct](https://ollama.com/library/qwen3:4b-instruct-2507-q4_K_M), and
[8B](https://ollama.com/library/qwen3:8b-q4_K_M) pages. Qwen3 was selected because
these instruction-capable variants fit the machine, accept structured prompts through
Ollama, and use the permissive Apache-2.0 license.

No 12–14B candidate was selected. The available Qwen3 14B Q4_K_M artifact is 9.3 GB;
adding it to the 9.1 GB selected set would exceed the 15 GiB free disk observed here,
and its weights alone would leave little of 16 GB unified memory for Ollama, prompt
context, and the OS. That does not meet the requirement that a larger model run
comfortably.

## Installation and download

1. If `ollama --version` is missing, install the macOS app from the official
   [Ollama download page](https://ollama.com/download), open it once, and confirm
   `ollama --version` in a new terminal.
2. Start Ollama with the menu-bar app or run `ollama serve` in a separate terminal.
3. Preview the pinned set with
   `PYTHONPATH=ml/src .venv/bin/python -m scamguard.model_setup --list`.
4. Ensure at least 10 GB is free, then run `make models`.

Model weights remain in Ollama's external storage and are never committed.


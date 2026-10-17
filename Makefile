PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
RUFF := $(if $(wildcard .venv/bin/ruff),.venv/bin/ruff,ruff)
MYPY := $(if $(wildcard .venv/bin/mypy),.venv/bin/mypy,mypy)
PYTEST := $(if $(wildcard .venv/bin/pytest),.venv/bin/pytest,pytest)

.PHONY: setup lint format typecheck test data eval

setup:
	@if command -v uv >/dev/null 2>&1; then \
		uv sync --extra dev; \
	else \
		python3 -m venv .venv; \
		.venv/bin/python -m pip install --upgrade pip; \
		.venv/bin/python -m pip install -e '.[dev]'; \
	fi

lint:
	$(RUFF) check ml/src ml/tests

format:
	$(RUFF) format ml/src ml/tests
	$(RUFF) check --fix ml/src ml/tests

typecheck:
	$(MYPY) ml/src ml/tests

test:
	$(PYTEST)

data:
	$(PYTHON) -m scamguard.data

eval: data
	$(PYTHON) -m scamguard.eval --model all --data data/eval/test_set.csv --out reports/

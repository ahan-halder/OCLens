.PHONY: test test-unit test-integration build-examples doctor lint format

test: test-unit test-integration

test-unit:
	pytest -q tests/unit

test-integration:
	pytest -q tests/integration --run-integration

build-examples:
	./scripts/build_examples.sh

doctor:
	oclens doctor --strict

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .

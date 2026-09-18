.PHONY: test test-unit test-integration build-examples doctor lint format verify verify-full

test: test-unit test-integration

verify:
	oclens verify

verify-full:
	oclens verify --full

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

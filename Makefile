.PHONY: test test-unit test-integration build-examples doctor

test: test-unit test-integration

test-unit:
	pytest -q tests/unit

test-integration:
	pytest -q tests/integration

build-examples:
	./scripts/build_examples.sh

doctor:
	oclens doctor --strict

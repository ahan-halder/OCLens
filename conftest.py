"""Root pytest configuration."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "integration: real GDB + PoCL tests (slow)",
    )


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests (skipped by default in full suite)",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.getoption("--run-integration"):
        return
    markexpr = config.getoption("-m") or ""
    if "integration" in markexpr:
        return
    skip = pytest.mark.skip(
        reason="integration tests skipped (use --run-integration or -m integration)"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip)

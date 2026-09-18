"""Shared OpenCL/PoCL environment for integration subprocesses."""

from __future__ import annotations

from pathlib import Path

import pytest

from oclens.constants import runtime_env_for_repo

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def oclens_subprocess_env() -> dict[str, str]:
    return runtime_env_for_repo(ROOT)

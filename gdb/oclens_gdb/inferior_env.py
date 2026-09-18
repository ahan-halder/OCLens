"""Push PoCL/OpenCL environment into the GDB inferior before run."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import gdb  # type: ignore[import-not-found]


def push_runtime_env_to_inferior() -> None:
    """Ensure kernel JIT (clang/ld) works under GDB, including minimal CI PATH."""
    repo = Path(os.environ.get("OCLENS_ROOT", ".")).resolve()
    src = repo / "src"
    if src.is_dir() and str(src) not in sys.path:
        sys.path.insert(0, str(src))

    from oclens.constants import RUNTIME_ENV_KEYS, runtime_env_for_repo

    merged = runtime_env_for_repo(repo)
    for key in RUNTIME_ENV_KEYS:
        value = merged.get(key)
        if value is None:
            continue
        gdb.execute(f"set environment {key} {value}")

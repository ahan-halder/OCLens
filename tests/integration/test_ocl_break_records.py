"""GDB batch-mode check that ocl-break is recorded without PoCL."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from oclens.constants import runtime_env_for_repo

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[2]
KERNEL = ROOT / "examples" / "stencil_barrier_bug" / "stencil_barrier_bug.cl"
SCRIPT = ROOT / "tests" / "fixtures" / "record_break.gdb"


@pytest.mark.skipif(shutil.which("gdb") is None, reason="gdb not installed")
def test_ocl_break_is_listed_in_batch_mode() -> None:
    exe = shutil.which("true") or "/bin/true"
    proc = subprocess.run(
        [
            "oclens",
            "debug",
            "--exe",
            exe,
            "--kernel",
            "stencil_barrier_bug",
            "--source",
            str(KERNEL),
            "--batch",
            str(SCRIPT),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
        env=runtime_env_for_repo(ROOT),
    )
    output = proc.stdout + proc.stderr
    assert "Breakpoint 1: stencil_barrier_bug.cl:23" in output, output
    assert "1: stencil_barrier_bug.cl:23" in output, output

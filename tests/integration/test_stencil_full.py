"""Full demo workflow: filtered breakpoint, locals, step (needs PoCL)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from oclens.constants import apply_local_pocl_prefix
from oclens.doctor import check_pocl_platform

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[2]
EXE = ROOT / "build" / "examples" / "stencil_barrier_bug" / "stencil_barrier_bug"
KERNEL = ROOT / "examples" / "stencil_barrier_bug" / "stencil_barrier_bug.cl"
SCRIPT = ROOT / "tests" / "fixtures" / "run_stencil_full.gdb"


def _pocl_ready() -> bool:
    apply_local_pocl_prefix(os.environ, ROOT / "pocl-install")
    return check_pocl_platform().ok and EXE.is_file()


@pytest.mark.skipif(shutil.which("gdb") is None, reason="gdb not installed")
@pytest.mark.skipif(not _pocl_ready(), reason="PoCL or stencil example not built")
def test_filtered_breakpoint_locals_and_step() -> None:
    proc = subprocess.run(
        [
            "oclens",
            "debug",
            "--exe",
            str(EXE),
            "--kernel",
            "stencil_barrier_bug",
            "--source",
            str(KERNEL),
            "--local-size",
            "8,1,1",
            "--batch",
            str(SCRIPT),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=90,
    )
    output = proc.stdout + proc.stderr
    assert "Selected work-item: global=(5, 0, 0)" in output, output
    assert "Stopped at stencil_barrier_bug.cl:23" in output, output
    assert "global = (5, 0, 0)" in output, output
    assert "private_value = 13" in output, output
    assert "left" in output and "11" in output, output
    assert "OCLENS_TEST:WORK_ITEM" in output, output
    assert "OCLENS_TEST:STEP" in output, output
    assert "OCLENS_TEST:PRINT" in output, output
    assert "\n2\n" in output, output

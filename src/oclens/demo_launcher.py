"""Launch the default stencil_barrier_bug interactive demo."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from oclens.debug_launcher import launch_debug_session, repo_root


def default_demo_paths(root: Path | None = None) -> tuple[Path, Path, Path]:
    base = root or repo_root()
    exe = base / "build" / "examples" / "stencil_barrier_bug" / "stencil_barrier_bug"
    source = base / "examples" / "stencil_barrier_bug" / "stencil_barrier_bug.cl"
    return exe, source, base


def launch_demo_session(batch: list[str] | None = None) -> int:
    root = repo_root()
    exe, source, _ = default_demo_paths(root)
    if not exe.is_file():
        print(
            f"error: demo binary not found: {exe}\n"
            "hint: cmake -S . -B build -G Ninja && cmake --build build",
            file=sys.stderr,
        )
        return 1
    if not source.is_file():
        print(f"error: demo kernel source not found: {source}", file=sys.stderr)
        return 1

    args = argparse.Namespace(
        exe=str(exe),
        kernel="stencil_barrier_bug",
        source=str(source),
        local_size="8,1,1",
        batch=batch,
    )
    return launch_debug_session(args)

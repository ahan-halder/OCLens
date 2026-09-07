#!/usr/bin/env python3
"""Probe PoCL-generated kernel symbols at runtime (Stage A ground truth)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True, help="Built host executable")
    parser.add_argument("--kernel", required=True, help="Kernel entry point name")
    args = parser.parse_args()

    if not args.exe.is_file():
        print(f"error: executable not found: {args.exe}", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env.setdefault("POCL_KERNEL_DEBUG_INFO", "1")
    env.setdefault("POCL_OPTIMIZATION", "0")
    env.setdefault("POCL_WORK_GROUP_METHOD", "loops")

    print(f"Running {args.exe} once to populate PoCL cache …")
    proc = subprocess.run([str(args.exe)], capture_output=True, text=True, env=env)
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")

    print(
        "\nNext step (manual, Stage A): attach GDB, break in the kernel work-group "
        f"function for '{args.kernel}', and record symbol names in docs/probe-pocl-7.2.md"
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run a host once and list PoCL-cached kernel sources that match a .cl file."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Allow running from a git checkout without installation.
_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "gdb"))

from oclens.constants import session_pocl_env  # noqa: E402
from oclens_gdb.source_mapper import find_cached_copy, iter_cached_cl_files  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True, help="Built host executable")
    parser.add_argument("--kernel", required=True, help="Kernel entry point name")
    parser.add_argument("--source", type=Path, help="Original .cl to match in the cache")
    args = parser.parse_args()

    exe = args.exe.resolve()
    if not exe.is_file():
        print(f"error: executable not found: {args.exe}", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env.update(session_pocl_env(prefix=_ROOT / "pocl-install"))
    cache = Path(env["POCL_CACHE_DIR"])
    cache.mkdir(parents=True, exist_ok=True)

    print(f"POCL_CACHE_DIR={cache}")
    print(f"Running {exe} once to populate PoCL cache …")
    proc = subprocess.run([str(exe)], capture_output=True, text=True, env=env, cwd=exe.parent)
    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")

    print("\nCached .cl files:")
    cl_files = iter_cached_cl_files([cache])
    if not cl_files:
        print("  (none — is PoCL installed and did the host run?)")
    for path in cl_files[:50]:
        print(f"  {path}")

    if args.source and args.source.is_file():
        match = find_cached_copy(args.source, roots=[cache])
        print(f"\nMatch for {args.source}:")
        print(f"  {match if match else '(no content match)'}")

    print(
        f"\nNext: gdb --args {exe} then `break {args.kernel}` and record "
        "locals in docs/probe-pocl-7.2.md"
    )
    return 0 if proc.returncode in (0, 1) else proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())

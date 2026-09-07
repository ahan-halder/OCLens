"""Launch GDB with the OCLens extension preloaded."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from oclens.constants import session_pocl_env


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def gdb_init_path() -> Path:
    return repo_root() / "gdb" / "oclens_gdb" / "init.gdb"


def build_debug_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env.update(session_pocl_env())
    if extra:
        env.update(extra)
    return env


def launch_debug_session(args: argparse.Namespace) -> int:
    gdb = shutil.which("gdb")
    if not gdb:
        print("error: gdb not found on PATH", file=sys.stderr)
        return 1

    init = gdb_init_path()
    if not init.is_file():
        print(f"error: missing GDB init script: {init}", file=sys.stderr)
        return 1

    exe = Path(args.exe).resolve()
    if not exe.is_file():
        print(f"error: executable not found: {exe}", file=sys.stderr)
        return 1

    source = Path(args.source).resolve()
    if not source.is_file():
        print(f"error: kernel source not found: {source}", file=sys.stderr)
        return 1

    cmd = [
        gdb,
        "--quiet",
        "-iex",
        f"source {init}",
        "-ex",
        f"oclens-session-set exe {exe}",
        "-ex",
        f"oclens-session-set kernel {args.kernel}",
        "-ex",
        f"oclens-session-set source {source}",
        "-ex",
        f"oclens-session-set local-size {args.local_size}",
    ]

    if args.batch:
        for script in args.batch:
            cmd.extend(["-x", script])
        cmd.append("-batch")
    else:
        cmd.extend(["-ex", "ocl-help"])

    env = build_debug_env(
        {
            "OCLENS_ROOT": str(repo_root()),
            "OCLENS_GDB_PKG": str(repo_root() / "gdb"),
        }
    )
    return subprocess.call(cmd, env=env)


def add_debug_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--exe", required=True, help="Host executable that enqueues the kernel")
    parser.add_argument("--kernel", required=True, help="OpenCL kernel entry point name")
    parser.add_argument("--source", required=True, help="Original .cl source file")
    parser.add_argument(
        "--local-size",
        default="8,1,1",
        help="Fixed local work size passed to the session (default: 8,1,1)",
    )
    parser.add_argument(
        "--batch",
        action="append",
        metavar="SCRIPT.gdb",
        help="Run a GDB command script (repeatable); implies non-interactive batch mode",
    )

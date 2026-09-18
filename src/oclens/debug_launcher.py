"""Launch GDB with the OCLens extension preloaded."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from oclens.constants import runtime_env_for_repo


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def gdb_init_path() -> Path:
    return repo_root() / "gdb" / "oclens_gdb" / "init.gdb"


def build_debug_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = runtime_env_for_repo(repo_root())
    if extra:
        env.update(extra)
    return env


def build_gdb_argv(
    gdb: str,
    init: Path,
    exe: Path,
    kernel: str,
    source: Path,
    local_size: str,
    batch_scripts: list[str] | None = None,
) -> list[str]:
    cmd = [
        gdb,
        "--quiet",
        "-iex",
        f"source {init}",
        "-ex",
        f"ocl-session-set exe {exe}",
        "-ex",
        f"ocl-session-set kernel {kernel}",
        "-ex",
        f"ocl-session-set source {source}",
        "-ex",
        f"ocl-session-set local-size {local_size}",
    ]
    if batch_scripts:
        for script in batch_scripts:
            cmd.extend(["-x", str(Path(script).resolve())])
        cmd.extend(["-batch", "--args", str(exe)])
    else:
        cmd.extend(["-ex", "ocl-help", "--args", str(exe)])
    return cmd


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

    cmd = build_gdb_argv(
        gdb,
        init,
        exe,
        args.kernel,
        source,
        args.local_size,
        args.batch,
    )

    env = build_debug_env(
        {
            "OCLENS_ROOT": str(repo_root()),
            "OCLENS_GDB_PKG": str(repo_root() / "gdb"),
        }
    )
    return subprocess.call(cmd, env=env)


def add_debug_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--exe", required=True, help="Host executable that enqueues the kernel"
    )
    parser.add_argument(
        "--kernel", required=True, help="OpenCL kernel entry point name"
    )
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

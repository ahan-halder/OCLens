"""End-to-end verification for judges and CI (`oclens verify`)."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from oclens.constants import configure_pocl_runtime_env, session_pocl_env
from oclens.debug_launcher import repo_root
from oclens.demo_launcher import default_demo_paths
from oclens.doctor import format_doctor_report


@dataclass(frozen=True)
class VerifyStep:
    name: str
    ok: bool
    detail: str = ""


def stencil_demo_exe(root: Path | None = None) -> Path:
    return default_demo_paths(root or repo_root())[0]


def verify_doctor(strict: bool = True) -> VerifyStep:
    report, code = format_doctor_report(strict=strict)
    ok = code == 0
    detail = "all required checks passed" if ok else "see doctor output above"
    if not ok:
        print(report, file=sys.stderr)
    return VerifyStep("Environment (oclens doctor)", ok, detail)


def verify_demo_binary_present(root: Path | None = None) -> VerifyStep:
    exe = stencil_demo_exe(root)
    ok = exe.is_file()
    detail = (
        str(exe)
        if ok
        else f"missing {exe} — run: cmake -S . -B build -G Ninja && cmake --build build"
    )
    return VerifyStep("Stencil example built", ok, detail)


def verify_demo_host_output(root: Path | None = None) -> VerifyStep:
    base = root or repo_root()
    exe = stencil_demo_exe(base)
    if not exe.is_file():
        return VerifyStep("Demo kernel host run", False, f"binary missing: {exe}")

    env = os.environ.copy()
    env.update(session_pocl_env(repo=base))
    configure_pocl_runtime_env(env, base)
    proc = subprocess.run(
        [str(exe)],
        check=False,
        capture_output=True,
        text=True,
        cwd=base,
        env=env,
        timeout=60,
    )
    output = proc.stdout + proc.stderr
    ok = (
        proc.returncode != 0
        and "gid=5" in output
        and "expected=24 actual=2" in output
        and "FAIL (intentional demo bug)" in output
    )
    detail = (
        "host confirms intentional bug at gid=5"
        if ok
        else f"unexpected output (exit {proc.returncode})"
    )
    if not ok:
        print(output, file=sys.stderr)
    return VerifyStep("Demo kernel host run", ok, detail)


def _run_pytest(args: list[str], root: Path) -> VerifyStep:
    label = " ".join(args)
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *args],
        check=False,
        cwd=root,
        timeout=300,
    )
    ok = proc.returncode == 0
    detail = "passed" if ok else f"exit code {proc.returncode}"
    return VerifyStep(f"pytest {label}", ok, detail)


def verify_unit_tests(root: Path | None = None) -> VerifyStep:
    base = root or repo_root()
    return _run_pytest(["-q", "tests/unit"], base)


def verify_integration_tests(root: Path | None = None) -> VerifyStep:
    base = root or repo_root()
    return _run_pytest(["-q", "tests/integration", "--run-integration"], base)


def verify_gdb_demo_batch(root: Path | None = None) -> VerifyStep:
    base = root or repo_root()
    script = base / "tests" / "fixtures" / "run_stencil_full.gdb"
    if not script.is_file():
        return VerifyStep("GDB demo batch workflow", False, f"missing {script}")

    env = os.environ.copy()
    configure_pocl_runtime_env(env, base)
    env["OCLENS_ROOT"] = str(base)
    env["OCLENS_GDB_PKG"] = str(base / "gdb")

    proc = subprocess.run(
        [
            "oclens",
            "demo",
            "--batch",
            str(script),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=base,
        env=env,
        timeout=120,
    )
    output = proc.stdout + proc.stderr
    ok = (
        proc.returncode == 0
        and "private_value = 13" in output
        and "global = (5, 0, 0)" in output
        and "\n2\n" in output
    )
    detail = (
        "filtered breakpoint, locals, step, print result" if ok else "batch demo failed"
    )
    if not ok:
        print(output, file=sys.stderr)
    return VerifyStep("GDB demo batch workflow", ok, detail)


def run_verify(
    *,
    full: bool = False,
    root: Path | None = None,
    steps: list[Callable[[], VerifyStep]] | None = None,
) -> tuple[str, int]:
    """Run verification steps and return a report plus exit code."""
    base = root or repo_root()

    def _doctor() -> VerifyStep:
        return verify_doctor(strict=True)

    def _binary() -> VerifyStep:
        return verify_demo_binary_present(base)

    def _host() -> VerifyStep:
        return verify_demo_host_output(base)

    def _unit() -> VerifyStep:
        return verify_unit_tests(base)

    if steps is not None:
        pipeline = steps
    else:
        pipeline = [_doctor, _binary, _host, _unit]
        if full:
            pipeline.append(lambda: verify_integration_tests(base))
            pipeline.append(lambda: verify_gdb_demo_batch(base))

    lines = ["OCLens verification"]
    failed = 0
    for run_step in pipeline:
        result = run_step()
        if not result.ok:
            failed += 1
        status = "ok" if result.ok else "FAIL"
        suffix = f" — {result.detail}" if result.detail else ""
        lines.append(f"[{status}] {result.name}{suffix}")

    if failed:
        lines.append("")
        lines.append(f"{failed} check(s) failed.")
    else:
        lines.append("")
        lines.append("All checks passed.")

    return "\n".join(lines), (1 if failed else 0)

"""Environment inspection helpers for `oclens doctor`."""

from __future__ import annotations

import ctypes
import os
import platform
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from oclens.constants import (
    POCL_TARGET_VERSION,
    apply_local_pocl_prefix,
    session_pocl_env,
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


def _run(
    cmd: list[str], *, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def check_linux() -> CheckResult:
    ok = platform.system() == "Linux"
    return CheckResult(
        "Linux", ok, platform.platform() if ok else "Linux required for v0.1"
    )


def check_python() -> CheckResult:
    version = sys.version.split()[0]
    ok = sys.version_info >= (3, 10)
    return CheckResult("Python", ok, f"{version} (>= 3.10 required)")


def check_gdb() -> CheckResult:
    gdb = shutil.which("gdb")
    if not gdb:
        return CheckResult("GDB found", False, "gdb not on PATH")
    proc = _run([gdb, "--version"])
    first = proc.stdout.splitlines()[0] if proc.stdout else gdb
    return CheckResult("GDB found", True, first)


def check_gdb_python_api() -> CheckResult:
    gdb = shutil.which("gdb")
    if not gdb:
        return CheckResult("GDB Python API available", False, "gdb not found")
    script = (
        "python import sys; print(getattr(sys, 'version_info', None) is not None); quit"
    )
    proc = _run([gdb, "-batch", "-ex", script])
    ok = proc.returncode == 0 and "True" in proc.stdout
    detail = (
        "embedded Python available"
        if ok
        else (proc.stderr.strip() or "GDB Python disabled")
    )
    return CheckResult("GDB Python API available", ok, detail)


def check_opencl_loader() -> CheckResult:
    candidates = [
        "libOpenCL.so.1",
        "libOpenCL.so",
        "OpenCL.dll",
    ]
    for name in candidates:
        try:
            ctypes.CDLL(name)
            return CheckResult("OpenCL loader found", True, name)
        except OSError:
            continue
    return CheckResult(
        "OpenCL loader found",
        False,
        "libOpenCL not loadable; install PoCL or an ICD loader",
    )


def _pocl_platform_info() -> tuple[bool, str, str]:
    """Return (found, version_string, detail)."""
    cl_uint = ctypes.c_uint
    cl_int = ctypes.c_int
    cl_platform_id = ctypes.c_void_p

    try:
        lib = ctypes.CDLL("libOpenCL.so.1")
    except OSError:
        try:
            lib = ctypes.CDLL("libOpenCL.so")
        except OSError as exc:
            return False, "", str(exc)

    lib.clGetPlatformIDs.argtypes = [cl_uint, ctypes.c_void_p, ctypes.POINTER(cl_uint)]
    lib.clGetPlatformIDs.restype = cl_int
    lib.clGetPlatformInfo.argtypes = [
        cl_platform_id,
        cl_uint,
        ctypes.c_size_t,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_size_t),
    ]
    lib.clGetPlatformInfo.restype = cl_int

    count = cl_uint()
    err = lib.clGetPlatformIDs(0, None, ctypes.byref(count))
    if err != 0 or count.value == 0:
        return False, "", f"clGetPlatformIDs failed (err={err})"

    CL_PLATFORM_VERSION = 0x0901
    CL_PLATFORM_NAME = 0x0902
    CL_PLATFORM_VENDOR = 0x0903

    platforms = (cl_platform_id * count.value)()
    err = lib.clGetPlatformIDs(count.value, platforms, None)
    if err != 0:
        return False, "", f"clGetPlatformIDs(enum) failed (err={err})"

    def info(platform: int, param: int) -> str:
        size = ctypes.c_size_t()
        err = lib.clGetPlatformInfo(platform, param, 0, None, ctypes.byref(size))
        if err != 0 or size.value == 0:
            return ""
        buf = ctypes.create_string_buffer(size.value)
        err = lib.clGetPlatformInfo(platform, param, size.value, buf, None)
        if err != 0:
            return ""
        return buf.value.decode(errors="replace")

    for i in range(count.value):
        platform = platforms[i]
        vendor = info(platform, CL_PLATFORM_VENDOR)
        name = info(platform, CL_PLATFORM_NAME)
        version = info(platform, CL_PLATFORM_VERSION)
        haystack = f"{vendor} {name} {version}".lower()
        if "pocl" in haystack:
            return True, version, f"{vendor} / {name}"

    return False, "", "no PoCL platform among OpenCL platforms"


def check_pocl_platform() -> CheckResult:
    found, version, detail = _pocl_platform_info()
    return CheckResult("PoCL platform found", found, detail or version)


def check_pocl_target_version() -> CheckResult:
    found, version, detail = _pocl_platform_info()
    if not found:
        return CheckResult(
            "PoCL target version recognised", False, "PoCL platform not found"
        )
    match = re.search(r"PoCL\s+([0-9.]+)", version, re.IGNORECASE)
    detected = match.group(1) if match else version.strip()
    ok = detected.startswith(POCL_TARGET_VERSION)
    return CheckResult(
        "PoCL target version recognised",
        ok,
        f"detected {detected!r}, expected {POCL_TARGET_VERSION!r}",
    )


def check_cpu_device() -> CheckResult:
    """Best-effort CPU device probe via clinfo when available."""
    clinfo = shutil.which("clinfo")
    if not clinfo:
        return CheckResult(
            "CPU device found",
            False,
            "clinfo not installed; install clinfo or verify manually",
        )
    proc = _run([clinfo])
    text = proc.stdout.lower()
    ok = "device type" in text and "cpu" in text
    return CheckResult(
        "CPU device found",
        ok,
        "PoCL CPU device reported by clinfo"
        if ok
        else "no CPU device in clinfo output",
    )


def check_gdb_extension() -> CheckResult:
    repo_root = Path(__file__).resolve().parents[2]
    init_py = repo_root / "gdb" / "oclens_gdb" / "__init__.py"
    ok = init_py.is_file()
    return CheckResult(
        "OCLens GDB extension present",
        ok,
        str(init_py) if ok else "gdb/oclens_gdb/__init__.py missing",
    )


def check_venv_recommendation() -> CheckResult:
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    return CheckResult(
        "Python virtualenv active",
        in_venv,
        "recommended: python3 -m venv .venv && source .venv/bin/activate",
    )


CORE_CHECKS: list[Callable[[], CheckResult]] = [
    check_linux,
    check_python,
    check_gdb,
    check_gdb_python_api,
    check_opencl_loader,
    check_pocl_platform,
    check_pocl_target_version,
    check_cpu_device,
    check_gdb_extension,
]

OPTIONAL_CHECKS: list[Callable[[], CheckResult]] = [
    check_venv_recommendation,
]


def format_doctor_report(*, strict: bool = False) -> tuple[str, int]:
    repo = Path(__file__).resolve().parents[2]
    apply_local_pocl_prefix(os.environ, repo / "pocl-install")

    lines = ["OCLens environment check"]
    failed = 0
    for check in CORE_CHECKS + OPTIONAL_CHECKS:
        result = check()
        if not result.ok and check in CORE_CHECKS:
            failed += 1
        status = "ok" if result.ok else "FAIL"
        suffix = f" — {result.detail}" if result.detail else ""
        lines.append(f"[{status}] {result.name}{suffix}")

    lines.append("")
    lines.append("PoCL debugger configuration:")
    for key, value in session_pocl_env(prefix=repo / "pocl-install").items():
        pretty = key.removeprefix("POCL_").lower().replace("_", " ")
        lines.append(f"  {pretty:28s}: {value}")

    if failed:
        lines.append("")
        lines.append(
            "Some required checks failed. See README Quick start: "
            "./scripts/bootstrap_ubuntu.sh && ./scripts/build_pocl.sh"
        )

    exit_code = failed if strict else 0
    return "\n".join(lines), exit_code

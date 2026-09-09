"""Pinned toolchain and PoCL configuration for OCLens v0.1."""

from __future__ import annotations

import os
from pathlib import Path

POCL_TARGET_VERSION = "7.2"
POCL_GIT_TAG = f"v{POCL_TARGET_VERSION}"

# Real PoCL 7.2 environment variables (see portablecl.org/docs/html/using.html
# and debug.html). Invented names such as POCL_KERNEL_DEBUG_INFO are ignored
# by PoCL and must not be used.
POCL_DEBUG_ENV: dict[str, str] = {
    "POCL_EXTRA_BUILD_FLAGS": "-g -cl-opt-disable",
    "POCL_LEAVE_KERNEL_COMPILER_TEMP_FILES": "1",
    "POCL_WORK_GROUP_METHOD": "loops",
    "POCL_WILOOPS_MAX_UNROLL_COUNT": "0",
    "POCL_CPU_MAX_CU_COUNT": "1",
    "POCL_KERNEL_CACHE": "1",
}


def default_pocl_cache_dir() -> Path:
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "oclens" / "pocl"


def apply_local_pocl_prefix(env: dict[str, str], prefix: Path) -> None:
    """Point the ICD loader at a repo-local pocl-install if present."""
    lib = prefix / "lib"
    vendors = prefix / "etc" / "OpenCL" / "vendors"
    if not (lib / "libpocl.so").exists() and not list(lib.glob("libpocl.so*")):
        return
    if vendors.is_dir() and "OPENCL_VENDOR_PATH" not in os.environ:
        env["OPENCL_VENDOR_PATH"] = str(vendors)
    if lib.is_dir():
        existing = env.get("LD_LIBRARY_PATH", "")
        env["LD_LIBRARY_PATH"] = f"{lib}:{existing}" if existing else str(lib)


def session_pocl_env(*, prefix: Path | None = None) -> dict[str, str]:
    env = dict(POCL_DEBUG_ENV)
    env.setdefault("POCL_CACHE_DIR", os.environ.get("POCL_CACHE_DIR", str(default_pocl_cache_dir())))
    if prefix is not None:
        apply_local_pocl_prefix(env, prefix)
    return env

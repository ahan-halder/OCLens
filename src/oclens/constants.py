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


def has_pocl_libraries(prefix: Path) -> bool:
    lib = prefix / "lib"
    return lib.is_dir() and bool(list(lib.glob("libpocl.so*")))


def ensure_pocl_icd_file(prefix: Path) -> None:
    """Write pocl.icd when PoCL was built with INSTALL_ICD=OFF."""
    if not has_pocl_libraries(prefix):
        return
    lib_dir = prefix / "lib"
    libs = sorted(lib_dir.glob("libpocl.so*"))
    if not libs:
        return
    vendors = prefix / "etc" / "OpenCL" / "vendors"
    vendors.mkdir(parents=True, exist_ok=True)
    icd = vendors / "pocl.icd"
    line = str(libs[-1].resolve())
    if not icd.is_file() or icd.read_text(encoding="utf-8").strip() != line:
        icd.write_text(f"{line}\n", encoding="utf-8")


def pocl_prefix_valid(prefix: Path) -> bool:
    if not has_pocl_libraries(prefix):
        return False
    ensure_pocl_icd_file(prefix)
    vendors = prefix / "etc" / "OpenCL" / "vendors"
    return vendors.is_dir() and any(vendors.iterdir())


def discover_pocl_prefix(repo: Path | None = None) -> Path | None:
    """Find a PoCL install: repo pocl-install, env override, or Docker /opt/pocl."""
    candidates: list[Path] = []
    if repo is not None:
        candidates.append(repo / "pocl-install")
    for key in ("POCL_INSTALL", "POCL_PREFIX"):
        value = os.environ.get(key)
        if value:
            candidates.append(Path(value))
    candidates.append(Path("/opt/pocl"))

    seen: set[Path] = set()
    for prefix in candidates:
        resolved = prefix.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if has_pocl_libraries(resolved):
            ensure_pocl_icd_file(resolved)
            return resolved
    return None


def apply_pocl_prefix_to_env(env: dict[str, str], prefix: Path) -> None:
    """Point the OpenCL ICD loader at a PoCL prefix."""
    if not has_pocl_libraries(prefix):
        return
    ensure_pocl_icd_file(prefix)
    lib = prefix / "lib"
    vendors = prefix / "etc" / "OpenCL" / "vendors"
    env["OPENCL_VENDOR_PATH"] = str(vendors)
    env["POCL_INSTALL"] = str(prefix)
    existing = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = f"{lib}:{existing}" if existing else str(lib)
    bin_dir = prefix / "bin"
    if bin_dir.is_dir():
        path = env.get("PATH", "")
        env["PATH"] = f"{bin_dir}:{path}" if path else str(bin_dir)


def configure_pocl_runtime_env(
    env: dict[str, str], repo: Path | None = None
) -> Path | None:
    """Apply PoCL library/vendor paths to env; return the prefix used."""
    prefix = discover_pocl_prefix(repo)
    if prefix is None:
        return None
    apply_pocl_prefix_to_env(env, prefix)
    return prefix


def apply_local_pocl_prefix(env: dict[str, str], prefix: Path) -> None:
    """Legacy helper: configure env when prefix is valid, else discover from repo parent."""
    if pocl_prefix_valid(prefix):
        apply_pocl_prefix_to_env(env, prefix)
        return
    parent = prefix.parent if prefix.name == "pocl-install" else None
    configure_pocl_runtime_env(env, parent)


def session_pocl_env(
    *, repo: Path | None = None, prefix: Path | None = None
) -> dict[str, str]:
    env = dict(POCL_DEBUG_ENV)
    env.setdefault(
        "POCL_CACHE_DIR",
        os.environ.get("POCL_CACHE_DIR", str(default_pocl_cache_dir())),
    )
    if prefix is not None and has_pocl_libraries(prefix):
        apply_pocl_prefix_to_env(env, prefix)
    elif repo is not None:
        configure_pocl_runtime_env(env, repo)
    return env

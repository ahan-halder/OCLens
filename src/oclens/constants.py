"""Pinned toolchain and PoCL configuration for OCLens v0.1."""

from __future__ import annotations

POCL_TARGET_VERSION = "7.2"
POCL_GIT_TAG = f"v{POCL_TARGET_VERSION}"

# Environment variables applied when launching PoCL-backed debug sessions.
POCL_DEBUG_ENV: dict[str, str] = {
    "POCL_DEBUG": "1",
    "POCL_KERNEL_DEBUG_INFO": "1",
    "POCL_OPTIMIZATION": "0",
    "POCL_WORK_GROUP_METHOD": "loops",
    "POCL_CPU_MAX_CU_COUNT": "1",
    "POCL_UNROLL_WI_LOOPS": "0",
}

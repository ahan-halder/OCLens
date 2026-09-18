"""PATH must stay usable for PoCL kernel JIT (clang needs ld on PATH)."""

from pathlib import Path

from oclens.constants import (
    apply_pocl_prefix_to_env,
    has_pocl_libraries,
    runtime_env_for_repo,
)


def test_apply_pocl_prefix_keeps_system_path_when_empty(tmp_path) -> None:
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "libpocl.so.2").write_text("", encoding="utf-8")
    vendors = tmp_path / "etc" / "OpenCL" / "vendors"
    vendors.mkdir(parents=True)
    (vendors / "pocl.icd").write_text(f"{lib}/libpocl.so.2\n", encoding="utf-8")
    (tmp_path / "bin").mkdir()

    env: dict[str, str] = {}
    apply_pocl_prefix_to_env(env, tmp_path)
    assert has_pocl_libraries(tmp_path)
    assert "/usr/bin" in env["PATH"]
    assert str(tmp_path / "bin") in env["PATH"]


def test_runtime_env_for_repo_keeps_system_path(tmp_path: Path) -> None:
    lib = tmp_path / "lib"
    lib.mkdir()
    (lib / "libpocl.so.2").write_text("", encoding="utf-8")
    vendors = tmp_path / "etc" / "OpenCL" / "vendors"
    vendors.mkdir(parents=True)
    (vendors / "pocl.icd").write_text(f"{lib}/libpocl.so.2\n", encoding="utf-8")
    (tmp_path / "bin").mkdir()

    env = runtime_env_for_repo(tmp_path, base={})
    assert "/usr/bin" in env["PATH"]

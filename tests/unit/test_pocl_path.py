"""PATH must stay usable for PoCL kernel JIT (clang needs ld on PATH)."""

from oclens.constants import apply_pocl_prefix_to_env, has_pocl_libraries


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

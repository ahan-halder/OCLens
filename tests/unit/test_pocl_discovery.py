"""PoCL prefix discovery for native vs Docker layouts."""

from pathlib import Path

from oclens.constants import (
    discover_pocl_prefix,
    ensure_pocl_icd_file,
    pocl_prefix_valid,
)


def _fake_pocl_tree(base: Path) -> Path:
    (base / "lib").mkdir(parents=True)
    (base / "lib" / "libpocl.so.2.14.0").write_text("", encoding="utf-8")
    vendors = base / "etc" / "OpenCL" / "vendors"
    vendors.mkdir(parents=True)
    (vendors / "pocl.icd").write_text(f"{base}/lib/libpocl.so.2\n", encoding="utf-8")
    return base


def test_pocl_prefix_valid_requires_lib_and_vendors(tmp_path: Path) -> None:
    assert not pocl_prefix_valid(tmp_path)
    install = _fake_pocl_tree(tmp_path / "pocl-install")
    assert pocl_prefix_valid(install)


def test_discover_prefers_repo_pocl_install(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    local = _fake_pocl_tree(repo / "pocl-install")
    other = _fake_pocl_tree(tmp_path / "other")
    monkeypatch.setenv("POCL_INSTALL", str(other))
    assert discover_pocl_prefix(repo) == local.resolve()


def test_ensure_pocl_icd_writes_vendor_file(tmp_path: Path) -> None:
    install = _fake_pocl_tree(tmp_path / "pocl")
    ensure_pocl_icd_file(install)
    icd = install / "etc" / "OpenCL" / "vendors" / "pocl.icd"
    assert icd.is_file()
    assert "libpocl.so" in icd.read_text(encoding="utf-8")


def test_discover_uses_env_when_no_local_tree(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    opt = _fake_pocl_tree(tmp_path / "opt-pocl")
    monkeypatch.setenv("POCL_INSTALL", str(opt))
    assert discover_pocl_prefix(repo) == opt.resolve()

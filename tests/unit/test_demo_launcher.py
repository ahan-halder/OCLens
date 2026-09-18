"""Tests for the default demo launcher."""

from pathlib import Path

from oclens.demo_launcher import default_demo_paths, launch_demo_session


def test_default_demo_paths_under_repo(tmp_path: Path) -> None:
    exe, source, base = default_demo_paths(tmp_path)
    assert base == tmp_path
    assert exe == tmp_path / "build/examples/stencil_barrier_bug/stencil_barrier_bug"
    assert source == tmp_path / "examples/stencil_barrier_bug/stencil_barrier_bug.cl"


def test_launch_demo_missing_binary_returns_one(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        "oclens.demo_launcher.repo_root",
        lambda: tmp_path,
    )
    assert launch_demo_session() == 1

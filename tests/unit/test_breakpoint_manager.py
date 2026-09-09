"""Tests for logical OpenCL source breakpoints."""

from pathlib import Path

import pytest

from oclens_gdb.breakpoint_manager import BreakpointManager, parse_break_spec


def test_parse_line_only(tmp_path: Path) -> None:
    source = tmp_path / "k.cl"
    source.write_text("//\n", encoding="utf-8")
    path, line = parse_break_spec("23", source)
    assert path == source
    assert line == 23


def test_parse_file_line(tmp_path: Path) -> None:
    path, line = parse_break_spec(f"{tmp_path / 'k.cl'}:9", None)
    assert path == tmp_path / "k.cl"
    assert line == 9


def test_parse_requires_source_for_bare_line() -> None:
    with pytest.raises(ValueError):
        parse_break_spec("10", None)


def test_manager_dedupes(tmp_path: Path) -> None:
    source = tmp_path / "k.cl"
    source.write_text("x\n", encoding="utf-8")
    mgr = BreakpointManager()
    a = mgr.add(source, 4)
    b = mgr.add(source, 4)
    assert a is b
    assert len(mgr.breakpoints) == 1

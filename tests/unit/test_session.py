"""Tests for shared GDB session state."""

from pathlib import Path

from oclens_gdb.session import SessionState, parse_size3


def test_parse_size3_pads_to_three() -> None:
    assert parse_size3("8") == (8, 1, 1)
    assert parse_size3("4,2") == (4, 2, 1)
    assert parse_size3("4,2,1") == (4, 2, 1)


def test_parse_size3_truncates_extra() -> None:
    assert parse_size3("1,2,3,4") == (1, 2, 3)


def test_format_info_lists_core_fields(tmp_path: Path) -> None:
    exe = tmp_path / "host"
    source = tmp_path / "kernel.cl"
    source.write_text("//\n", encoding="utf-8")
    session = SessionState(
        exe=exe,
        kernel="vector_add",
        source=source,
        local_size=(8, 1, 1),
    )
    text = session.format_info()
    assert "OCLens session" in text
    assert f"executable : {exe}" in text
    assert "kernel     : vector_add" in text
    assert f"source     : {source}" in text
    assert "local size : (8, 1, 1)" in text
    assert "selected WI: (none)" in text

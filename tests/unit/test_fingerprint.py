"""Tests for kernel source fingerprinting."""

from pathlib import Path

from oclens_gdb.fingerprint import fingerprint_file, fingerprint_text, normalize_source


def test_normalize_newlines() -> None:
    assert normalize_source("a\r\nb\rc") == "a\nb\nc"


def test_fingerprint_ignores_crlf() -> None:
    assert fingerprint_text("int x;\n") == fingerprint_text("int x;\r\n")


def test_fingerprint_file(tmp_path: Path) -> None:
    p = tmp_path / "k.cl"
    p.write_text("__kernel void k() {}\n", encoding="utf-8")
    assert fingerprint_file(p) == fingerprint_text("__kernel void k() {}\n")

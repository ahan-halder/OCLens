"""Tests for projecting PoCL context arrays to source scalars."""

from oclens_gdb.value_projector import project_scalar


def test_scalar_passthrough() -> None:
    assert project_scalar("12", 5) == "12"


def test_nested_context_array() -> None:
    assert project_scalar("{{{12, 14, 16, 18, 20, 22, 24, 26}}}", 5) == "22"


def test_flat_brace_array() -> None:
    assert project_scalar("{0, 1, 2, 3}", 2) == "2"


def test_out_of_range_keeps_raw_when_ambiguous() -> None:
    assert project_scalar("{1, 2, 3}", 9) == "{1, 2, 3}"

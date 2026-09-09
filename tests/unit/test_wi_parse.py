"""Tests for ocl-wi argument parsing."""

from oclens_gdb.wi_parse import identity_from_global, parse_wi_command


def test_parse_global_short() -> None:
    wi = parse_wi_command("global 5", (8, 1, 1))
    assert wi.global_id == (5, 0, 0)
    assert wi.local_id == (5, 0, 0)
    assert wi.group_id == (0, 0, 0)


def test_parse_second_group() -> None:
    wi = parse_wi_command("global 9", (8, 1, 1))
    assert wi.group_id == (1, 0, 0)
    assert wi.local_id == (1, 0, 0)


def test_parse_local_group() -> None:
    wi = parse_wi_command("local 1 group 1", (8, 1, 1))
    assert wi.global_id == (9, 0, 0)


def test_show_and_clear() -> None:
    assert parse_wi_command("show", (8, 1, 1)) == "show"
    assert parse_wi_command("clear", (8, 1, 1)) == "clear"


def test_identity_from_global_matches() -> None:
    wi = identity_from_global((5, 0, 0), (8, 1, 1))
    assert wi.local_id[0] == 5


def test_serial_hit_maps_second_group() -> None:
    from oclens_gdb.wi_parse import identity_from_serial_hit, linear_local_index

    wi = identity_from_serial_hit(5, (8, 1, 1))
    assert wi.global_id == (5, 0, 0)
    wi = identity_from_serial_hit(9, (8, 1, 1))
    assert wi.global_id == (9, 0, 0)
    assert wi.group_id == (1, 0, 0)
    assert wi.local_id == (1, 0, 0)
    assert linear_local_index((5, 0, 0), (8, 1, 1)) == 5

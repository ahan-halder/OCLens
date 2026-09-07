"""Unit tests for OpenCL work-item coordinate math."""

from oclens_gdb.coords import global_from_group_local, group_from_global, local_from_global


def test_global_group_local_roundtrip() -> None:
    local_size = (8, 1, 1)
    group = (0, 0, 0)
    local = (5, 0, 0)
    global_id = global_from_group_local(group, local, local_size)
    assert global_id == (5, 0, 0)
    assert group_from_global(global_id, local_size) == group
    assert local_from_global(global_id, local_size) == local


def test_second_work_group() -> None:
    local_size = (8, 1, 1)
    group = (1, 0, 0)
    local = (1, 0, 0)
    assert global_from_group_local(group, local, local_size) == (9, 0, 0)

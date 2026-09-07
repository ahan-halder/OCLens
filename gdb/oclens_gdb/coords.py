"""Pure coordinate math used by WorkItemTracker and breakpoint filtering."""

from __future__ import annotations


def global_from_group_local(
    group: tuple[int, int, int],
    local: tuple[int, int, int],
    local_size: tuple[int, int, int],
) -> tuple[int, int, int]:
    return (
        group[0] * local_size[0] + local[0],
        group[1] * local_size[1] + local[1],
        group[2] * local_size[2] + local[2],
    )


def group_from_global(
    global_id: tuple[int, int, int],
    local_size: tuple[int, int, int],
) -> tuple[int, int, int]:
    return (
        global_id[0] // local_size[0],
        global_id[1] // local_size[1],
        global_id[2] // local_size[2],
    )


def local_from_global(
    global_id: tuple[int, int, int],
    local_size: tuple[int, int, int],
) -> tuple[int, int, int]:
    return (
        global_id[0] % local_size[0],
        global_id[1] % local_size[1],
        global_id[2] % local_size[2],
    )

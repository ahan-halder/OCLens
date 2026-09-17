"""PoCL-specific symbol and layout knowledge (version-pinned v7.2)."""

from __future__ import annotations

from oclens_gdb.coords import (
    global_from_group_local,
    group_from_global,
    local_from_global,
)
from oclens_gdb.wi_parse import identity_from_serial_hit
from oclens_gdb.work_item_tracker import WorkItemIdentity

# Names emitted by PoCL's WorkitemHandler / WorkitemLoops for the loops method.
LOCAL_ID_SYMS = ("_local_id_x", "_local_id_y", "_local_id_z")
GLOBAL_ID_SYMS = ("_global_id_x", "_global_id_y", "_global_id_z")
GROUP_ID_SYMS = ("_group_id_x", "_group_id_y", "_group_id_z")
SOURCE_GID = ("gid", "global_id")
SOURCE_LID = ("lid", "local_id")


def _eval_int(expr: str) -> int | None:
    try:
        import gdb  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        value = gdb.parse_and_eval(expr)
        return int(value)
    except Exception:  # noqa: BLE001 - GDB raises gdb.error and sometimes ValueError
        return None


def _eval_triple(names: tuple[str, str, str]) -> tuple[int, int, int] | None:
    vals: list[int] = []
    for name in names:
        got = _eval_int(name)
        if got is None:
            if not vals:
                return None
            vals.append(0)
        else:
            vals.append(got)
    return (vals[0], vals[1], vals[2])


class PoclAdapter:
    """Isolate PoCL version-specific probing behind one adapter."""

    TARGET_VERSION = "7.2"

    def __init__(self, local_size: tuple[int, int, int] = (8, 1, 1)) -> None:
        self.local_size = local_size

    def read_current_work_item(self) -> WorkItemIdentity:
        local = _eval_triple(LOCAL_ID_SYMS)
        glob = _eval_triple(GLOBAL_ID_SYMS)
        group = _eval_triple(GROUP_ID_SYMS)

        if glob is None:
            gid0 = _eval_int("gid")
            if gid0 is not None:
                glob = (gid0, 0, 0)

        if local is None:
            lid0 = _eval_int("lid")
            if lid0 is not None:
                local = (lid0, 0, 0)

        if glob is not None and local is None:
            local = local_from_global(glob, self.local_size)
        if glob is not None and group is None:
            group = group_from_global(glob, self.local_size)
        if local is not None and group is not None and glob is None:
            glob = global_from_group_local(group, local, self.local_size)
        if local is not None and glob is None:
            glob = local
            group = (0, 0, 0)

        if glob is None or local is None or group is None:
            raise RuntimeError(
                "could not read OpenCL work-item IDs from the current frame"
            )
        return WorkItemIdentity(global_id=glob, group_id=group, local_id=local)

    def identity_from_hit(self, hit_index: int) -> WorkItemIdentity:
        return identity_from_serial_hit(hit_index, self.local_size)

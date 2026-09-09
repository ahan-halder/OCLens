"""Parse ocl-wi arguments and compare identities."""

from __future__ import annotations

from oclens_gdb.coords import global_from_group_local, group_from_global, local_from_global
from oclens_gdb.work_item_tracker import WorkItemIdentity


def linear_local_index(local_id: tuple[int, int, int], local_size: tuple[int, int, int]) -> int:
    return (
        local_id[0]
        + local_id[1] * local_size[0]
        + local_id[2] * local_size[0] * local_size[1]
    )


def unflatten_local(index: int, local_size: tuple[int, int, int]) -> tuple[int, int, int]:
    x = index % local_size[0]
    y = (index // local_size[0]) % local_size[1]
    z = index // (local_size[0] * local_size[1])
    return (x, y, z)


def identity_from_serial_hit(
    hit_index: int,
    local_size: tuple[int, int, int],
) -> WorkItemIdentity:
    """Map sequential loops-method hits onto work-item IDs (1-D group grid)."""
    nlocal = max(1, local_size[0] * local_size[1] * local_size[2])
    local_lin = hit_index % nlocal
    group_x = hit_index // nlocal
    local = unflatten_local(local_lin, local_size)
    group = (group_x, 0, 0)
    return identity_from_local_group(local, group, local_size)


def identity_from_global(
    global_id: tuple[int, int, int],
    local_size: tuple[int, int, int],
) -> WorkItemIdentity:
    return WorkItemIdentity(
        global_id=global_id,
        group_id=group_from_global(global_id, local_size),
        local_id=local_from_global(global_id, local_size),
    )


def identity_from_local_group(
    local_id: tuple[int, int, int],
    group_id: tuple[int, int, int],
    local_size: tuple[int, int, int],
) -> WorkItemIdentity:
    return WorkItemIdentity(
        global_id=global_from_group_local(group_id, local_id, local_size),
        group_id=group_id,
        local_id=local_id,
    )


def parse_wi_command(argument: str, local_size: tuple[int, int, int]) -> WorkItemIdentity | str:
    """Return a WorkItemIdentity, or 'show'/'clear'."""
    tokens = argument.replace("=", " ").replace(",", " ").split()
    if not tokens or tokens[0] in {"show", "status"}:
        return "show"
    if tokens[0] == "clear":
        return "clear"
    if tokens[0] == "global":
        nums = [int(t) for t in tokens[1:] if t.lstrip("+-").isdigit()]
        if not nums:
            raise ValueError("usage: ocl-wi global <x>[,y,z]")
        while len(nums) < 3:
            nums.append(0)
        gid = (nums[0], nums[1], nums[2])
        return identity_from_global(gid, local_size)
    if tokens[0] == "local":
        # ocl-wi local x[,y,z] group x[,y,z]
        if "group" in tokens:
            gi = tokens.index("group")
            local_toks = tokens[1:gi]
            group_toks = tokens[gi + 1 :]
        else:
            local_toks = tokens[1:]
            group_toks = []
        local_nums = [int(t) for t in local_toks if t.lstrip("+-").isdigit()]
        group_nums = [int(t) for t in group_toks if t.lstrip("+-").isdigit()]
        while len(local_nums) < 3:
            local_nums.append(0)
        while len(group_nums) < 3:
            group_nums.append(0)
        return identity_from_local_group(
            (local_nums[0], local_nums[1], local_nums[2]),
            (group_nums[0], group_nums[1], group_nums[2]),
            local_size,
        )
    # Bare numbers: treat as global id
    nums = [int(t) for t in tokens if t.lstrip("+-").isdigit()]
    if nums:
        while len(nums) < 3:
            nums.append(0)
        return identity_from_global((nums[0], nums[1], nums[2]), local_size)
    raise ValueError("usage: ocl-wi global <x>[,y,z] | ocl-wi local <x> group <g> | ocl-wi show | ocl-wi clear")

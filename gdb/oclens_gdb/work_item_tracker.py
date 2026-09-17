"""Track selected vs active OpenCL work-items (Stage D)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkItemIdentity:
    global_id: tuple[int, int, int]
    group_id: tuple[int, int, int]
    local_id: tuple[int, int, int]

    def format(self) -> str:
        return (
            "Work-item:\n"
            f"  global = {self.global_id}\n"
            f"  group  = {self.group_id}\n"
            f"  local  = {self.local_id}"
        )


def step_loop_done(
    start_wi: WorkItemIdentity | None,
    start_line: int | None,
    current_wi: WorkItemIdentity | None,
    current_line: int | None,
) -> bool:
    """Return True when a work-item-preserving step should stop."""
    if start_wi is None:
        return True
    if current_wi is not None and current_wi.global_id == start_wi.global_id:
        return current_line != start_line
    return False


class WorkItemTracker:
    def __init__(self) -> None:
        self.selected: WorkItemIdentity | None = None
        self.active: WorkItemIdentity | None = None

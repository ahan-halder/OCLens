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


class WorkItemTracker:
    def __init__(self) -> None:
        self.selected: WorkItemIdentity | None = None
        self.active: WorkItemIdentity | None = None

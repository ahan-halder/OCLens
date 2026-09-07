"""Track selected vs active OpenCL work-items (Stage D)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkItemIdentity:
    global_id: tuple[int, int, int]
    group_id: tuple[int, int, int]
    local_id: tuple[int, int, int]


class WorkItemTracker:
    def __init__(self) -> None:
        self.selected: WorkItemIdentity | None = None
        self.active: WorkItemIdentity | None = None

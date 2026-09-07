"""Work-item filtered breakpoints (Stage E)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class WorkItemBreakpoint:
    source: Path
    line: int
    selected_global: tuple[int, int, int] | None = None

    def matches_selection(self, active_global: tuple[int, int, int]) -> bool:
        if self.selected_global is None:
            return True
        return self.selected_global == active_global

"""Shared session state for an OCLens debug session."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from oclens_gdb.breakpoint_manager import BreakpointManager
from oclens_gdb.source_mapper import SourceMapper


@dataclass
class WorkItemSelection:
    mode: str = "none"  # none | global | local
    global_id: tuple[int, int, int] = (0, 0, 0)
    group_id: tuple[int, int, int] = (0, 0, 0)
    local_id: tuple[int, int, int] = (0, 0, 0)


@dataclass
class SessionState:
    exe: Path | None = None
    kernel: str = ""
    source: Path | None = None
    local_size: tuple[int, int, int] = (8, 1, 1)
    selection: WorkItemSelection = field(default_factory=WorkItemSelection)
    extension_loaded: bool = True
    mapper: SourceMapper | None = None
    breakpoints: BreakpointManager = field(default_factory=BreakpointManager)

    def ensure_mapper(self) -> SourceMapper:
        if self.source is None:
            raise RuntimeError("session source is not set")
        if self.mapper is None or self.mapper.original != self.source.resolve():
            self.mapper = SourceMapper(self.source)
        return self.mapper

    def format_info(self) -> str:
        lines = [
            "OCLens session",
            f"  executable : {self.exe or '(unset)'}",
            f"  kernel     : {self.kernel or '(unset)'}",
            f"  source     : {self.source or '(unset)'}",
            f"  local size : {self.local_size}",
        ]
        mapper = self.mapper
        runtime = mapper.runtime if mapper is not None else None
        lines.append(f"  runtime    : {runtime or '(unbound)'}")
        sel = self.selection
        if sel.mode == "global":
            lines.append(f"  selected WI: global={sel.global_id}")
        elif sel.mode == "local":
            lines.append(
                f"  selected WI: local={sel.local_id} group={sel.group_id}"
            )
        else:
            lines.append("  selected WI: (none)")
        return "\n".join(lines)


SESSION = SessionState()


def parse_size3(text: str) -> tuple[int, int, int]:
    parts = [int(p.strip()) for p in text.split(",")]
    while len(parts) < 3:
        parts.append(1)
    return tuple(parts[:3])  # type: ignore[return-value]

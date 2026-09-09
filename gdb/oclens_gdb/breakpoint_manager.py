"""Logical source breakpoints, independent of GDB's pending .so load."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def parse_break_spec(text: str, default_source: Path | None) -> tuple[Path, int]:
    spec = text.strip()
    if not spec:
        raise ValueError("empty breakpoint spec")
    if ":" in spec:
        file_part, line_part = spec.rsplit(":", 1)
        if not file_part:
            raise ValueError(f"missing file in spec: {text!r}")
        return Path(file_part), int(line_part)
    if default_source is None:
        raise ValueError("pass <file>:<line> or set a session source first")
    return default_source, int(spec)


@dataclass
class WorkItemBreakpoint:
    source: Path
    line: int
    selected_global: tuple[int, int, int] | None = None
    gdb_number: int | None = None

    def spec(self) -> str:
        return f"{self.source}:{self.line}"

    def matches_selection(self, active_global: tuple[int, int, int]) -> bool:
        if self.selected_global is None:
            return True
        return self.selected_global == active_global


@dataclass
class BreakpointManager:
    breakpoints: list[WorkItemBreakpoint] = field(default_factory=list)

    def add(self, source: Path, line: int) -> WorkItemBreakpoint:
        existing = self.find(source, line)
        if existing is not None:
            return existing
        bp = WorkItemBreakpoint(source=source.resolve(), line=line)
        self.breakpoints.append(bp)
        return bp

    def find(self, source: Path, line: int) -> WorkItemBreakpoint | None:
        resolved = source.resolve()
        for bp in self.breakpoints:
            if bp.source == resolved and bp.line == line:
                return bp
        return None

    def format_list(self) -> str:
        if not self.breakpoints:
            return "(no breakpoints)"
        lines = []
        for i, bp in enumerate(self.breakpoints, start=1):
            lines.append(f"{i}: {bp.source.name}:{bp.line}")
        return "\n".join(lines)

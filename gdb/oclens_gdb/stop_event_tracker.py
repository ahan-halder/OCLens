"""Normalize GDB stop reasons for OCLens (Stage G).

StopEventTracker classifies why the inferior stopped and provides
human-readable formatting used by ``report_stop`` and ``ocl-continue``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StopReason(Enum):
    """Coarse classification of why GDB halted the inferior."""

    BREAKPOINT = "breakpoint"
    SIGNAL = "signal"
    EXIT = "exit"
    STEP = "step"
    UNKNOWN = "unknown"


@dataclass
class StopEvent:
    reason: StopReason
    source_line: int | None = None
    signal_name: str | None = None
    exit_code: int | None = None
    detail: str = ""

    def format_reason(self) -> str:
        """One-line human-readable stop reason."""
        if self.reason is StopReason.BREAKPOINT:
            return "breakpoint"
        if self.reason is StopReason.SIGNAL:
            sig = self.signal_name or "unknown"
            return f"signal {sig}"
        if self.reason is StopReason.EXIT:
            code = self.exit_code if self.exit_code is not None else "?"
            return f"exited (code {code})"
        if self.reason is StopReason.STEP:
            return "end of step"
        return self.detail or "unknown"

    def format(self, source_name: str = "kernel") -> str:
        """Human-readable stop summary (location + reason)."""
        if self.source_line is None:
            header = "Stopped (no source line available)"
        else:
            header = f"Stopped at {source_name}:{self.source_line}"
        return f"{header}\nReason: {self.format_reason()}"


class StopEventTracker:
    """Track the most recent stop event for the session."""

    def __init__(self) -> None:
        self.last: StopEvent | None = None

    def record_breakpoint(self, source_line: int | None = None) -> StopEvent:
        event = StopEvent(reason=StopReason.BREAKPOINT, source_line=source_line)
        self.last = event
        return event

    def record_signal(
        self, signal_name: str, source_line: int | None = None
    ) -> StopEvent:
        event = StopEvent(
            reason=StopReason.SIGNAL,
            source_line=source_line,
            signal_name=signal_name,
        )
        self.last = event
        return event

    def record_exit(self, exit_code: int | None = None) -> StopEvent:
        event = StopEvent(reason=StopReason.EXIT, exit_code=exit_code)
        self.last = event
        return event

    def record_step(self, source_line: int | None = None) -> StopEvent:
        event = StopEvent(reason=StopReason.STEP, source_line=source_line)
        self.last = event
        return event

    def classify_gdb_stop(self, gdb_reason: str) -> StopReason:
        """Map a GDB stop-reason string to our enum.

        GDB's Python API exposes stop reasons such as ``breakpoint-hit``,
        ``end-stepping-range``, ``signal-received``, and ``exited-normally``.
        """
        lowered = gdb_reason.lower()
        if "breakpoint" in lowered:
            return StopReason.BREAKPOINT
        if "step" in lowered or "end-stepping" in lowered:
            return StopReason.STEP
        if "signal" in lowered:
            return StopReason.SIGNAL
        if "exit" in lowered:
            return StopReason.EXIT
        return StopReason.UNKNOWN

    def record_from_gdb_reason(
        self,
        gdb_reason: str,
        *,
        source_line: int | None = None,
        signal_name: str | None = None,
        exit_code: int | None = None,
        detail: str = "",
    ) -> StopEvent:
        """Classify a GDB stop-reason string and record the matching event."""
        kind = self.classify_gdb_stop(gdb_reason)
        if kind is StopReason.BREAKPOINT:
            return self.record_breakpoint(source_line)
        if kind is StopReason.STEP:
            return self.record_step(source_line)
        if kind is StopReason.SIGNAL:
            return self.record_signal(signal_name or "unknown", source_line)
        if kind is StopReason.EXIT:
            return self.record_exit(exit_code)
        event = StopEvent(
            reason=StopReason.UNKNOWN,
            source_line=source_line,
            detail=detail or gdb_reason,
        )
        self.last = event
        return event

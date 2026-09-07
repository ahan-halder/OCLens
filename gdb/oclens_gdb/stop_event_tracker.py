"""Normalize GDB stop reasons for OCLens (Stage G)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StopEvent:
    reason: str
    source_line: int | None = None

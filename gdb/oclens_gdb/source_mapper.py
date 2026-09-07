"""Map user .cl sources to PoCL's cached runtime copies (Stage C)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceMapping:
    original: Path
    runtime: Path | None = None


class SourceMapper:
    """Bind original kernel sources to PoCL runtime cache paths."""

    def __init__(self, original: Path) -> None:
        self.original = original.resolve()
        self.runtime: Path | None = None

    def bind_runtime(self, runtime_path: Path) -> None:
        self.runtime = runtime_path.resolve()

    def is_bound(self) -> bool:
        return self.runtime is not None

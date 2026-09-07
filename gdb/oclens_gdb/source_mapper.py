"""Map user .cl sources to PoCL's cached runtime copies."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from oclens_gdb.fingerprint import fingerprint_file, fingerprint_text


def default_cache_roots() -> list[Path]:
    roots: list[Path] = []
    env = os.environ.get("POCL_CACHE_DIR")
    if env:
        roots.append(Path(env))
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        roots.append(Path(xdg) / "pocl" / "kcache")
        roots.append(Path(xdg) / "oclens" / "pocl")
    home_cache = Path.home() / ".cache"
    roots.append(home_cache / "pocl" / "kcache")
    roots.append(home_cache / "oclens" / "pocl")
    seen: set[Path] = set()
    unique: list[Path] = []
    for root in roots:
        resolved = root.expanduser()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)
    return unique


def iter_cached_cl_files(roots: list[Path] | None = None) -> list[Path]:
    found: list[Path] = []
    for root in roots or default_cache_roots():
        if not root.is_dir():
            continue
        found.extend(path for path in root.rglob("*.cl") if path.is_file())
    found.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return found


def find_cached_copy(
    original: Path,
    *,
    roots: list[Path] | None = None,
    extra_candidates: list[Path] | None = None,
) -> Path | None:
    """Return the newest cache file whose contents match `original`."""
    target = fingerprint_file(original)
    candidates = list(extra_candidates or [])
    candidates.extend(iter_cached_cl_files(roots))
    for path in candidates:
        if path.resolve() == original.resolve():
            continue
        try:
            if fingerprint_file(path) == target:
                return path.resolve()
        except OSError:
            continue
    return None


def find_cached_copy_from_text(
    source_text: str,
    *,
    roots: list[Path] | None = None,
) -> Path | None:
    target = fingerprint_text(source_text)
    for path in iter_cached_cl_files(roots):
        try:
            if fingerprint_file(path) == target:
                return path.resolve()
        except OSError:
            continue
    return None


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

    def bind_from_cache(self, roots: list[Path] | None = None) -> Path | None:
        match = find_cached_copy(self.original, roots=roots)
        if match is not None:
            self.runtime = match
        return match

    def bind_from_path_hint(self, hinted: str | Path) -> Path | None:
        """Accept a DWARF / GDB filename, which is often a PoCL tempfile."""
        path = Path(str(hinted)).resolve()
        if path.is_file():
            self.runtime = path
            return path
        return None

    def is_bound(self) -> bool:
        return self.runtime is not None

    def gdb_break_location(self, line: int) -> str:
        """Location string GDB should use (runtime file if bound)."""
        source = self.runtime if self.runtime is not None else self.original
        return f"{source}:{line}"

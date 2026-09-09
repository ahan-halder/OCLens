"""Read source-level locals from the current GDB frame."""

from __future__ import annotations

import gdb  # type: ignore[import-not-found]

from oclens_gdb.pocl_adapter import PoclAdapter
from oclens_gdb.session import SESSION
from oclens_gdb.value_projector import project_scalar
from oclens_gdb.wi_parse import linear_local_index

_SKIP_PREFIXES = ("_", ".", "pocl")


def _skip_name(name: str) -> bool:
    lowered = name.lower()
    return lowered.startswith(_SKIP_PREFIXES) or lowered in {
        "this",
        "self",
    }


def _local_index() -> int:
    active = SESSION.tracker.active
    if active is not None:
        return linear_local_index(active.local_id, SESSION.local_size)
    try:
        wi = PoclAdapter(SESSION.local_size).read_current_work_item()
        return linear_local_index(wi.local_id, SESSION.local_size)
    except Exception:
        return 0


def iter_frame_symbols() -> list[tuple[str, str]]:
    frame = gdb.selected_frame()
    block = frame.block()
    seen: set[str] = set()
    rows: list[tuple[str, str]] = []
    index = _local_index()
    while block is not None:
        for sym in block:
            name = sym.name
            if name in seen or _skip_name(name):
                continue
            if not (sym.is_variable or sym.is_argument):
                continue
            seen.add(name)
            try:
                raw = str(frame.read_var(sym))
            except gdb.error:
                continue
            rows.append((name, project_scalar(raw, index)))
        block = block.superblock
    return rows


def format_locals() -> str:
    rows = iter_frame_symbols()
    if not rows:
        return "(no locals)"
    width = max(len(name) for name, _ in rows)
    return "\n".join(f"{name:<{width}} = {value}" for name, value in rows)


def print_identifier(name: str) -> str:
    index = _local_index()
    try:
        raw = str(gdb.parse_and_eval(name))
    except gdb.error as exc:
        return f"error: {exc}"
    return project_scalar(raw, index)

"""Project PoCL context-array storage to source-level scalars."""

from __future__ import annotations

import re

_NUMBER = re.compile(r"[-+]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")


def flatten_numeric_leaves(raw: str) -> list[str]:
    """Extract scalar leaves from GDB prints like `{{{12, 14, 16}}}`."""
    cleaned = re.sub(r"[{}()]", " ", raw)
    leaves: list[str] = []
    for chunk in cleaned.split(","):
        tok = chunk.strip().split()[-1] if chunk.strip() else ""
        tok = tok.rstrip("ulUL")
        if tok and _NUMBER.fullmatch(tok):
            leaves.append(tok)
    return leaves


def project_scalar(raw_repr: str, local_index: int) -> str:
    """Pick the work-item element from a PoCL context array, or return as-is."""
    text = raw_repr.strip()
    if not text:
        return text
    if "{" in text:
        leaves = flatten_numeric_leaves(text)
        if not leaves:
            return text
        if 0 <= local_index < len(leaves):
            return leaves[local_index]
        if len(leaves) == 1:
            return leaves[0]
        return text
    return text


class ValueProjector:
    """Translate PoCL per-work-item private storage into source-level values."""

    def project_scalar(self, raw_repr: str, local_index: int) -> str:
        return project_scalar(raw_repr, local_index)

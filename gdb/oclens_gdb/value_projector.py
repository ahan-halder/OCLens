"""Project PoCL context-array storage to source scalars (Stage F)."""

from __future__ import annotations


class ValueProjector:
    """Translate PoCL per-work-item private storage into source-level values."""

    def project_scalar(self, raw_repr: str, local_index: int) -> str:
        raise NotImplementedError("Stage F — ValueProjector not implemented yet")

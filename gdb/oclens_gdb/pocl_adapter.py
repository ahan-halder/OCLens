"""PoCL-specific symbol and layout knowledge (version-pinned v7.2)."""

from __future__ import annotations

from oclens_gdb.work_item_tracker import WorkItemIdentity


class PoclAdapter:
    """Isolate PoCL version-specific probing behind one adapter."""

    TARGET_VERSION = "7.2"

    def read_current_work_item(self) -> WorkItemIdentity:
        raise NotImplementedError("Stage D — PoclAdapter.read_current_work_item")

"""GDB breakpoint that ignores work-items other than the session selection."""

from __future__ import annotations

import gdb  # type: ignore[import-not-found]

from oclens_gdb.pocl_adapter import PoclAdapter
from oclens_gdb.session import SESSION


class WorkItemFilterBreakpoint(gdb.Breakpoint):
    def stop(self) -> bool:  # type: ignore[override]
        adapter = PoclAdapter(SESSION.local_size)
        try:
            wi = adapter.read_current_work_item()
        except Exception:
            wi = adapter.identity_from_hit(SESSION.serial_hit)
            SESSION.serial_hit += 1
        SESSION.tracker.active = wi
        sel = SESSION.selection
        if sel.mode == "none":
            return True
        if sel.mode == "global":
            return wi.global_id == sel.global_id
        if sel.mode == "local":
            return wi.local_id == sel.local_id and wi.group_id == sel.group_id
        return True

"""Work-item-preserving source stepping."""

from __future__ import annotations

import gdb  # type: ignore[import-not-found]
from oclens_gdb.kernel_control import current_sal, report_stop
from oclens_gdb.pocl_adapter import PoclAdapter
from oclens_gdb.session import SESSION
from oclens_gdb.work_item_tracker import WorkItemIdentity, step_loop_done


def _alive() -> bool:
    inf = gdb.selected_inferior()
    return bool(inf.is_valid() and inf.pid)


def _current_wi() -> WorkItemIdentity | None:
    if SESSION.tracker.active is not None:
        return SESSION.tracker.active
    try:
        return PoclAdapter(SESSION.local_size).read_current_work_item()
    except Exception:
        return None


def step_preserving(command: str, *, max_hops: int = 512) -> None:
    """Run gdb `next`/`step` until the active work-item advances a source line."""
    start_wi = _current_wi()
    _, start_line = current_sal()
    gdb.execute(command)
    hops = 0
    while _alive() and hops < max_hops:
        hops += 1
        wi = _current_wi()
        _, line = current_sal()
        if step_loop_done(start_wi, start_line, wi, line):
            break
        gdb.execute(command)
    if start_wi is not None:
        SESSION.tracker.active = _current_wi() or start_wi
    report_stop(reason="step")


class StepController:
    def step_source_next(self) -> None:
        step_preserving("next")

    def step_source_step(self) -> None:
        step_preserving("step")

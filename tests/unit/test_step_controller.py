"""Tests for work-item-preserving step loop logic."""

from oclens_gdb.work_item_tracker import WorkItemIdentity, step_loop_done


def _wi(gx: int, gy: int = 0, gz: int = 0) -> WorkItemIdentity:
    return WorkItemIdentity(
        global_id=(gx, gy, gz),
        group_id=(0, 0, 0),
        local_id=(0, 0, 0),
    )


def test_step_loop_done_without_start_wi() -> None:
    assert step_loop_done(None, 10, _wi(0), 11) is True


def test_step_loop_done_same_wi_same_line() -> None:
    start = _wi(3)
    assert step_loop_done(start, 10, start, 10) is False


def test_step_loop_done_same_wi_new_line() -> None:
    start = _wi(3)
    assert step_loop_done(start, 10, start, 11) is True


def test_step_loop_done_different_wi() -> None:
    start = _wi(3)
    assert step_loop_done(start, 10, _wi(4), 11) is False

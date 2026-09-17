"""Tests for GDB stop-event classification and formatting."""

from oclens_gdb.stop_event_tracker import (
    StopEvent,
    StopEventTracker,
    StopReason,
)


def test_format_reason_breakpoint() -> None:
    event = StopEvent(reason=StopReason.BREAKPOINT, source_line=12)
    assert event.format_reason() == "breakpoint"


def test_format_reason_signal() -> None:
    event = StopEvent(reason=StopReason.SIGNAL, signal_name="SIGSEGV")
    assert event.format_reason() == "signal SIGSEGV"


def test_format_reason_exit() -> None:
    event = StopEvent(reason=StopReason.EXIT, exit_code=0)
    assert event.format_reason() == "exited (code 0)"


def test_format_reason_step() -> None:
    event = StopEvent(reason=StopReason.STEP)
    assert event.format_reason() == "end of step"


def test_format_includes_location_and_reason() -> None:
    event = StopEvent(reason=StopReason.BREAKPOINT, source_line=23)
    text = event.format(source_name="kernel.cl")
    assert text == "Stopped at kernel.cl:23\nReason: breakpoint"


def test_classify_gdb_stop() -> None:
    tracker = StopEventTracker()
    assert tracker.classify_gdb_stop("breakpoint-hit") is StopReason.BREAKPOINT
    assert tracker.classify_gdb_stop("end-stepping-range") is StopReason.STEP
    assert tracker.classify_gdb_stop("signal-received") is StopReason.SIGNAL
    assert tracker.classify_gdb_stop("exited-normally") is StopReason.EXIT
    assert tracker.classify_gdb_stop("something-else") is StopReason.UNKNOWN


def test_record_from_gdb_reason() -> None:
    tracker = StopEventTracker()
    event = tracker.record_from_gdb_reason(
        "signal-received",
        source_line=5,
        signal_name="SIGTRAP",
    )
    assert event.reason is StopReason.SIGNAL
    assert event.signal_name == "SIGTRAP"
    assert tracker.last is event


def test_tracker_records_last_event() -> None:
    tracker = StopEventTracker()
    bp = tracker.record_breakpoint(source_line=10)
    tracker.record_step(source_line=11)
    assert tracker.last is not bp
    assert tracker.last is not None
    assert tracker.last.reason is StopReason.STEP

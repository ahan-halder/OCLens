"""Start execution and bind kernel sources after the PoCL .so loads."""

from __future__ import annotations

import re

import gdb  # type: ignore[import-not-found]
from oclens_gdb.filtered_break import WorkItemFilterBreakpoint
from oclens_gdb.inferior_env import push_runtime_env_to_inferior
from oclens_gdb.pocl_adapter import PoclAdapter
from oclens_gdb.session import SESSION


def current_sal() -> tuple[str | None, int | None]:
    try:
        frame = gdb.selected_frame()
    except gdb.error:
        return None, None
    sal = frame.find_sal()
    filename = None
    if sal.symtab is not None:
        filename = sal.symtab.fullname() or sal.symtab.filename
    line = int(sal.line) if sal.line else None
    return filename, line


def bind_sources_from_stop() -> None:
    mapper = SESSION.ensure_mapper()
    hinted, _line = current_sal()
    if hinted:
        mapper.bind_from_path_hint(hinted)
    if not mapper.is_bound():
        mapper.bind_from_cache()
    gdb.write("OCLens: kernel object loaded\n")
    if mapper.is_bound():
        gdb.write("OCLens: source mapped\n")
        gdb.write(f"  original: {mapper.original}\n")
        gdb.write(f"  runtime : {mapper.runtime}\n")
        if not mapper.fingerprints_match():
            gdb.write(
                "OCLens: warning: runtime source differs from the session .cl "
                "(rebuild the example so the copied kernel is up to date)\n"
            )
    else:
        gdb.write(
            "OCLens: could not bind a PoCL cache copy; using original source path\n"
        )


def _line_is_code(location: str) -> bool:
    try:
        text = gdb.execute(f"info line {location}", to_string=True)
    except gdb.error:
        return False
    lowered = text.lower()
    if "no line" in lowered or "out of range" in lowered:
        return False
    return "line" in lowered


def _plant_breakpoint(path: str, line: int) -> tuple[int, gdb.Breakpoint]:
    candidates = [line]
    if line > 1:
        candidates.append(line - 1)
    candidates.append(line + 1)
    for candidate in candidates:
        loc = f"{path}:{candidate}"
        if not _line_is_code(loc):
            continue
        created = WorkItemFilterBreakpoint(loc)
        return candidate, created
    created = WorkItemFilterBreakpoint(f"{path}:{line}")
    return line, created


def install_line_breakpoints() -> None:
    mapper = SESSION.ensure_mapper()
    gdb.execute("set breakpoint pending on", to_string=True)
    path = str(mapper.runtime or mapper.original)
    for bp in SESSION.breakpoints.breakpoints:
        planted_line, created = _plant_breakpoint(path, bp.line)
        bp.gdb_number = int(created.number)
        if planted_line != bp.line:
            gdb.write(
                f"OCLens: no code at line {bp.line}, breakpoint at {planted_line}\n"
            )


def _signal_name(sig_num: int) -> str:
    try:
        import signal

        return signal.Signals(sig_num).name
    except (ValueError, AttributeError, ImportError):
        return f"SIG{sig_num}"


def detect_gdb_stop() -> tuple[str, str | None, int | None]:
    """Inspect GDB state and return ``(reason, signal_name, exit_code)``."""
    inf = gdb.selected_inferior()
    if not inf.is_valid() or not inf.pid:
        exit_code: int | None = None
        try:
            text = gdb.execute("info program", to_string=True)
            match = re.search(r"exit code\s+(-?\d+)", text, re.IGNORECASE)
            if match:
                exit_code = int(match.group(1))
        except gdb.error:
            pass
        return "exited-normally", None, exit_code

    try:
        text = gdb.execute("info program", to_string=True)
    except gdb.error:
        return "unknown", None, None

    lowered = text.lower()
    if "breakpoint" in lowered:
        return "breakpoint-hit", None, None
    if "step" in lowered or "stepping" in lowered:
        return "end-stepping-range", None, None
    if "exited" in lowered:
        exit_code = None
        match = re.search(r"exit code\s+(-?\d+)", text, re.IGNORECASE)
        if match:
            exit_code = int(match.group(1))
        return "exited-normally", None, exit_code
    if "signal" in lowered:
        match = re.search(r"signal\s+(\S+)", text, re.IGNORECASE)
        signal_name = match.group(1) if match else None
        return "signal-received", signal_name, None

    try:
        thread = gdb.selected_thread()
        if thread is not None:
            sig_num = thread.stop_signal()
            if sig_num:
                return "signal-received", _signal_name(sig_num), None
    except gdb.error:
        pass

    return "unknown", None, None


def original_source_line(line: int) -> str | None:
    path = SESSION.source
    if path is None or not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1]
    return None


def report_stop(*, reason: str | None = None) -> None:
    _filename, line = current_sal()
    name = SESSION.source.name if SESSION.source else "kernel"
    tracker = SESSION.stop_tracker
    if reason is None:
        gdb_reason, signal_name, exit_code = detect_gdb_stop()
        event = tracker.record_from_gdb_reason(
            gdb_reason,
            source_line=line,
            signal_name=signal_name,
            exit_code=exit_code,
        )
    elif reason == "step":
        event = tracker.record_step(source_line=line)
    elif reason == "breakpoint":
        event = tracker.record_breakpoint(source_line=line)
    else:
        event = tracker.record_from_gdb_reason(reason, source_line=line)
    gdb.write(event.format(source_name=name) + "\n")
    if line is None:
        return
    wi = SESSION.tracker.active
    if wi is None:
        try:
            wi = PoclAdapter(SESSION.local_size).read_current_work_item()
            SESSION.tracker.active = wi
        except Exception:
            wi = None
    if wi is not None:
        gdb.write(wi.format() + "\n")
    text = original_source_line(line)
    if text is not None:
        gdb.write(f"{line}  {text}\n")


def run_until_kernel() -> None:
    inf = gdb.selected_inferior()
    if inf.pid:
        raise RuntimeError("inferior already running; use ocl-continue")
    if not SESSION.kernel:
        raise RuntimeError("session kernel is not set")
    push_runtime_env_to_inferior()
    gdb.execute("set breakpoint pending on", to_string=True)
    SESSION.serial_hit = 0
    SESSION.tracker.active = None
    entry = gdb.Breakpoint(SESSION.kernel, temporary=True)
    gdb.execute("run")
    bind_sources_from_stop()
    if SESSION.breakpoints.breakpoints:
        _, line = current_sal()
        install_line_breakpoints()
        wanted = {bp.line for bp in SESSION.breakpoints.breakpoints}
        if entry.is_valid():
            entry.delete()
        if line not in wanted:
            gdb.execute("continue")
    else:
        gdb.write("No source breakpoints set; stopped at kernel entry.\n")
    report_stop()

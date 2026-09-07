"""Start execution and bind kernel sources after the PoCL .so loads."""

from __future__ import annotations

from pathlib import Path

import gdb  # type: ignore[import-not-found]

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
    else:
        gdb.write("OCLens: could not bind a PoCL cache copy; using original source path\n")


def install_line_breakpoints() -> None:
    mapper = SESSION.ensure_mapper()
    gdb.execute("set breakpoint pending on", to_string=True)
    for bp in SESSION.breakpoints.breakpoints:
        loc = mapper.gdb_break_location(bp.line)
        created = gdb.Breakpoint(loc)
        bp.gdb_number = int(created.number)


def original_source_line(line: int) -> str | None:
    path = SESSION.source
    if path is None or not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if 1 <= line <= len(lines):
        return lines[line - 1]
    return None


def report_stop() -> None:
    _filename, line = current_sal()
    name = SESSION.source.name if SESSION.source else "kernel"
    if line is None:
        gdb.write("Stopped (no source line available)\n")
        return
    gdb.write(f"Stopped at {name}:{line}\n")
    gdb.write("Reason: breakpoint\n")
    text = original_source_line(line)
    if text is not None:
        gdb.write(f"{line}  {text}\n")


def run_until_kernel() -> None:
    inf = gdb.selected_inferior()
    if inf.pid:
        raise RuntimeError("inferior already running; use ocl-continue")
    if not SESSION.kernel:
        raise RuntimeError("session kernel is not set")
    gdb.execute("set breakpoint pending on", to_string=True)
    entry = gdb.Breakpoint(SESSION.kernel)
    gdb.execute("run")
    try:
        bind_sources_from_stop()
        if SESSION.breakpoints.breakpoints:
            _, line = current_sal()
            wanted = {bp.line for bp in SESSION.breakpoints.breakpoints}
            install_line_breakpoints()
            entry.delete()
            if line not in wanted:
                gdb.execute("continue")
        else:
            gdb.write("No source breakpoints set; stopped at kernel entry.\n")
    finally:
        pass
    report_stop()

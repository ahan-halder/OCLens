"""Start execution and bind kernel sources after the PoCL .so loads."""

from __future__ import annotations

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
        if not mapper.fingerprints_match():
            gdb.write(
                "OCLens: warning: runtime source differs from the session .cl "
                "(rebuild the example so the copied kernel is up to date)\n"
            )
    else:
        gdb.write("OCLens: could not bind a PoCL cache copy; using original source path\n")


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
        created = gdb.Breakpoint(loc)
        return candidate, created
    created = gdb.Breakpoint(f"{path}:{line}")
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

"""GDB user commands for OCLens."""

from __future__ import annotations

try:
    import gdb  # type: ignore[import-not-found]
except ImportError as exc:  # pragma: no cover - only importable inside GDB
    raise ImportError("oclens_gdb.commands must be imported from inside GDB") from exc

from pathlib import Path

from oclens_gdb.breakpoint_manager import parse_break_spec
from oclens_gdb.inspect import format_locals, print_identifier
from oclens_gdb.kernel_control import report_stop, run_until_kernel
from oclens_gdb.session import SESSION, parse_size3
from oclens_gdb.step_controller import StepController
from oclens_gdb.wi_parse import parse_wi_command


class OclHelp(gdb.Command):
    """List OCLens commands."""

    def __init__(self) -> None:
        super().__init__("ocl-help", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        gdb.write(
            "\n".join(
                [
                    "OCLens commands:",
                    "  ocl-help",
                    "  ocl-info",
                    "  ocl-session-set <key> <value...>",
                    "  ocl-break <line> | ocl-break <file>:<line>",
                    "  ocl-breaks",
                    "  ocl-wi global <x>[,y,z]",
                    "  ocl-wi local <x>[,y,z] group <x>[,y,z]",
                    "  ocl-wi show | ocl-wi clear",
                    "  ocl-run",
                    "  ocl-continue",
                    "  ocl-next | ocl-step",
                    "  ocl-locals",
                    "  ocl-print <identifier>",
                    "  ocl-eval <gdb-expression>",
                    "",
                ]
            )
        )


class OclInfo(gdb.Command):
    """Show current OCLens session state."""

    def __init__(self) -> None:
        super().__init__("ocl-info", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        gdb.write(SESSION.format_info() + "\n")
        active = SESSION.tracker.active
        if active is not None:
            gdb.write("Active " + active.format() + "\n")


class OclSessionSet(gdb.Command):
    """Set session fields: exe, kernel, source, local-size."""

    def __init__(self) -> None:
        super().__init__("ocl-session-set", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        parts = argument.split()
        if len(parts) < 2:
            gdb.write("usage: ocl-session-set <exe|kernel|source|local-size> <value...>\n")
            return
        key, *rest = parts
        value = " ".join(rest)
        if key == "exe":
            SESSION.exe = Path(value)
        elif key == "kernel":
            SESSION.kernel = value
        elif key == "source":
            SESSION.source = Path(value)
            SESSION.mapper = None
        elif key == "local-size":
            SESSION.local_size = parse_size3(value)
        else:
            gdb.write(f"unknown session key: {key}\n")


class OclBreak(gdb.Command):
    """Set a logical source-line breakpoint in the OpenCL kernel."""

    def __init__(self) -> None:
        super().__init__("ocl-break", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        try:
            source, line = parse_break_spec(argument, SESSION.source)
        except ValueError as exc:
            gdb.write(f"usage: ocl-break <line> | ocl-break <file>:<line>\n{exc}\n")
            return
        bp = SESSION.breakpoints.add(source, line)
        gdb.write(
            f"Breakpoint {SESSION.breakpoints.breakpoints.index(bp) + 1}: "
            f"{bp.source.name}:{bp.line}\n"
        )


class OclBreaks(gdb.Command):
    """List logical OCLens breakpoints."""

    def __init__(self) -> None:
        super().__init__("ocl-breaks", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        gdb.write(SESSION.breakpoints.format_list() + "\n")


class OclWi(gdb.Command):
    """Select which OpenCL work-item future stops should match."""

    def __init__(self) -> None:
        super().__init__("ocl-wi", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        try:
            result = parse_wi_command(argument, SESSION.local_size)
        except ValueError as exc:
            gdb.write(f"{exc}\n")
            return
        if result == "show":
            sel = SESSION.selection
            if sel.mode == "none":
                gdb.write("Selected work-item: (none)\n")
            else:
                gdb.write(f"Selected work-item: global={sel.global_id}\n")
            active = SESSION.tracker.active
            if active is not None and (
                sel.mode == "none" or active.global_id != sel.global_id
            ):
                gdb.write("Current machine state still belongs to:\n")
                gdb.write(f"  global={active.global_id}\n")
            return
        if result == "clear":
            SESSION.selection.mode = "none"
            SESSION.tracker.selected = None
            gdb.write("Work-item selection cleared.\n")
            return
        SESSION.tracker.selected = result
        SESSION.selection.mode = "global"
        SESSION.selection.global_id = result.global_id
        SESSION.selection.local_id = result.local_id
        SESSION.selection.group_id = result.group_id
        active = SESSION.tracker.active
        if active is not None and active.global_id != result.global_id:
            gdb.write(f"Selected future work-item: global={result.global_id}\n")
            gdb.write("Current machine state still belongs to:\n")
            gdb.write(f"  global={active.global_id}\n")
            gdb.write("Continue or restart to reach a source stop for the new selection.\n")
        else:
            gdb.write(f"Selected work-item: global={result.global_id}\n")


class OclRun(gdb.Command):
    """Run the host until the kernel loads, bind sources, then hit ocl-break."""

    def __init__(self) -> None:
        super().__init__("ocl-run", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        try:
            run_until_kernel()
        except Exception as exc:  # noqa: BLE001
            gdb.write(f"ocl-run failed: {exc}\n")


class OclContinue(gdb.Command):
    """Continue inferior execution."""

    def __init__(self) -> None:
        super().__init__("ocl-continue", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        gdb.execute("continue")
        inf = gdb.selected_inferior()
        if inf.is_valid() and inf.pid:
            report_stop()


class OclNext(gdb.Command):
    """Source next, staying on the active work-item."""

    def __init__(self) -> None:
        super().__init__("ocl-next", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        StepController().step_source_next()


class OclStep(gdb.Command):
    """Source step, staying on the active work-item."""

    def __init__(self) -> None:
        super().__init__("ocl-step", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        StepController().step_source_step()


class OclLocals(gdb.Command):
    """Print source-level locals for the active work-item."""

    def __init__(self) -> None:
        super().__init__("ocl-locals", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        try:
            gdb.write(format_locals() + "\n")
        except Exception as exc:  # noqa: BLE001
            gdb.write(f"ocl-locals failed: {exc}\n")


class OclPrint(gdb.Command):
    """Print one identifier, projected for the active work-item."""

    def __init__(self) -> None:
        super().__init__("ocl-print", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        name = argument.strip()
        if not name:
            gdb.write("usage: ocl-print <identifier>\n")
            return
        gdb.write(print_identifier(name) + "\n")


class OclEval(gdb.Command):
    """Delegate an expression to GDB."""

    def __init__(self) -> None:
        super().__init__("ocl-eval", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        gdb.execute(f"print {argument}")


def register_commands() -> None:
    OclHelp()
    OclInfo()
    OclSessionSet()
    OclBreak()
    OclBreaks()
    OclWi()
    OclRun()
    OclContinue()
    OclNext()
    OclStep()
    OclLocals()
    OclPrint()
    OclEval()


register_commands()

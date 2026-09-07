"""GDB user commands for OCLens."""

from __future__ import annotations

try:
    import gdb  # type: ignore[import-not-found]
except ImportError as exc:  # pragma: no cover - only importable inside GDB
    raise ImportError("oclens_gdb.commands must be imported from inside GDB") from exc

from pathlib import Path

from oclens_gdb.breakpoint_manager import parse_break_spec
from oclens_gdb.kernel_control import run_until_kernel
from oclens_gdb.session import SESSION, parse_size3


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
                    "  ocl-run",
                    "  ocl-continue",
                    "  ocl-wi           (not implemented yet)",
                    "  ocl-locals       (not implemented yet)",
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
        gdb.write(f"Breakpoint {SESSION.breakpoints.breakpoints.index(bp) + 1}: {bp.source.name}:{bp.line}\n")


class OclBreaks(gdb.Command):
    """List logical OCLens breakpoints."""

    def __init__(self) -> None:
        super().__init__("ocl-breaks", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        gdb.write(SESSION.breakpoints.format_list() + "\n")


class OclRun(gdb.Command):
    """Run the host until the kernel loads, bind sources, then hit ocl-break."""

    def __init__(self) -> None:
        super().__init__("ocl-run", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        try:
            run_until_kernel()
        except Exception as exc:  # noqa: BLE001 - surface GDB/runtime errors to the prompt
            gdb.write(f"ocl-run failed: {exc}\n")


class OclContinue(gdb.Command):
    """Continue inferior execution."""

    def __init__(self) -> None:
        super().__init__("ocl-continue", gdb.COMMAND_USER)

    def invoke(self, argument: str, from_tty: bool) -> None:
        gdb.execute("continue")


def register_commands() -> None:
    OclHelp()
    OclInfo()
    OclSessionSet()
    OclBreak()
    OclBreaks()
    OclRun()
    OclContinue()


register_commands()

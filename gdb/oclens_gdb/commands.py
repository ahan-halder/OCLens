"""GDB user commands for OCLens (Stage B skeleton)."""

from __future__ import annotations

try:
    import gdb  # type: ignore[import-not-found]
except ImportError as exc:  # pragma: no cover - only importable inside GDB
    raise ImportError("oclens_gdb must be imported from inside GDB") from exc

from pathlib import Path

from oclens_gdb.session import SESSION, parse_size3


class OclHelp(gdb.Command):
    """List OCLens commands."""

    def __init__(self) -> None:
        super().__init__("ocl-help", gdb.COMMAND_USER, prefix=True)

    def invoke(self, argument: str, from_tty: bool) -> None:
        gdb.write(
            "\n".join(
                [
                    "OCLens commands (v0.1 skeleton):",
                    "  ocl-help",
                    "  ocl-info",
                    "  ocl-session-set <key> <value...>",
                    "  ocl-run          (Stage C+ — not implemented yet)",
                    "  ocl-break        (Stage C+ — not implemented yet)",
                    "  ocl-wi           (Stage D+ — not implemented yet)",
                    "  ocl-locals       (Stage F+ — not implemented yet)",
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
        elif key == "local-size":
            SESSION.local_size = parse_size3(value)
        else:
            gdb.write(f"unknown session key: {key}\n")


def register_commands() -> None:
    OclHelp()
    OclInfo()
    OclSessionSet()


register_commands()

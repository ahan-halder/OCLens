"""OCLens GDB Python extension — OpenCL semantic layer on top of GDB."""

from __future__ import annotations

__version__ = "0.1.1"


def register_extension() -> None:
    """Import command registrations. Call only from inside GDB."""
    from oclens_gdb import commands as _commands  # noqa: F401

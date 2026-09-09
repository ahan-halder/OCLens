"""Tests for GDB argv construction."""

from pathlib import Path

from oclens.debug_launcher import build_gdb_argv


def test_interactive_argv_loads_host_and_uses_ocl_session_set() -> None:
    argv = build_gdb_argv(
        "gdb",
        Path("/repo/gdb/oclens_gdb/init.gdb"),
        Path("/repo/build/host"),
        "vector_add",
        Path("/repo/kernel.cl"),
        "8,1,1",
        None,
    )
    assert argv[-2:] == ["--args", "/repo/build/host"]
    assert "ocl-session-set kernel vector_add" in argv
    assert "oclens-session-set" not in " ".join(argv)


def test_batch_argv_places_scripts_before_args() -> None:
    script = Path("script.gdb")
    argv = build_gdb_argv(
        "gdb",
        Path("/init.gdb"),
        Path("/host"),
        "k",
        Path("/k.cl"),
        "8,1,1",
        [str(script)],
    )
    x_at = argv.index("-x")
    args_at = argv.index("--args")
    assert argv[x_at : x_at + 2] == ["-x", str(script.resolve())]
    assert x_at < args_at
    assert argv[args_at:] == ["--args", "/host"]
    assert "-batch" in argv
    assert argv.index("-batch") < args_at

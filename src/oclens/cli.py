"""OCLens command-line interface."""

from __future__ import annotations

import argparse

from oclens import __version__
from oclens.debug_launcher import add_debug_arguments, launch_debug_session
from oclens.demo_launcher import launch_demo_session
from oclens.doctor import format_doctor_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oclens",
        description="Work-item-aware source debugging for OpenCL kernels on PoCL",
    )
    parser.add_argument("--version", action="version", version=f"oclens {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Verify toolchain, PoCL, and GDB extension")
    doctor.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when a required check fails",
    )

    debug = sub.add_parser("debug", help="Launch GDB with the OCLens extension loaded")
    add_debug_arguments(debug)

    demo = sub.add_parser(
        "demo",
        help="Launch GDB on the stencil_barrier_bug example (same as scripts/run_demo.sh)",
    )
    demo.add_argument(
        "--batch",
        action="append",
        metavar="SCRIPT.gdb",
        help="Run a GDB command script (repeatable); implies non-interactive batch mode",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        report, code = format_doctor_report(strict=args.strict)
        print(report)
        return code

    if args.command == "debug":
        return launch_debug_session(args)

    if args.command == "demo":
        return launch_demo_session(batch=args.batch)

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

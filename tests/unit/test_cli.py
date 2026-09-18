"""CLI wiring tests."""

from oclens.cli import build_parser


def test_verify_subcommand_full_flag() -> None:
    args = build_parser().parse_args(["verify", "--full"])
    assert args.command == "verify"
    assert args.full is True


def test_verify_subcommand_default() -> None:
    args = build_parser().parse_args(["verify"])
    assert args.command == "verify"
    assert args.full is False

"""CLI entrypoint for jarvis."""

from __future__ import annotations

import argparse

from jarvis.doctor import format_diagnostics


def build_parser() -> argparse.ArgumentParser:
    """Build command-line parser."""
    parser = argparse.ArgumentParser(prog="jarvis", description="Jarvis assistant CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("doctor", help="Print environment diagnostics")

    return parser


def main() -> int:
    """Run the jarvis CLI."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "doctor":
        print(format_diagnostics())
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

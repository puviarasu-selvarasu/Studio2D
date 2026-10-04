"""Studio2D command-line entry point."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from app import __version__
from app.core.doctor import inspect_required_tools


def run_doctor() -> int:
    statuses = inspect_required_tools()

    print()
    print("Studio2D Runtime Doctor")
    print("=======================")
    print()

    for status in statuses:
        marker = "OK" if status.ok else "FAIL"

        print(f"[{marker}] {status.name}")
        print(f"       command : {status.command}")
        print(f"       path    : {status.path or 'NOT FOUND'}")
        print(f"       version : {status.version}")
        print()

    failed = [status for status in statuses if not status.ok]

    if failed:
        print(
            f"Runtime check FAILED: "
            f"{len(failed)} required tool(s) unavailable."
        )
        return 1

    print("Runtime check PASSED.")
    print("All Phase 0 external tools are available.")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="studio2d",
        description="Studio2D local anime production studio.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Studio2D {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "doctor",
        help="Check required local production tools.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        return run_doctor()

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

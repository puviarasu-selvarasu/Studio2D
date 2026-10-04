"""Studio2D command-line entry point."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from app import __version__
from app.blender.runner import run_blender_probe
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

    failed = [
        status
        for status in statuses
        if not status.ok
    ]

    if failed:
        print(
            "Runtime check FAILED: "
            f"{len(failed)} required tool(s) unavailable."
        )
        return 1

    print("Runtime check PASSED.")
    print("All Phase 0 external tools are available.")

    return 0


def run_blender_runtime_probe() -> int:
    print()
    print("Studio2D Blender Runtime Probe")
    print("==============================")
    print()

    result = run_blender_probe()

    if not result.success:
        print("[FAIL] Blender process bridge")

        if result.returncode is not None:
            print(
                f"       returncode : {result.returncode}"
            )

        if result.error:
            print(f"       error      : {result.error}")

        if result.stderr.strip():
            print()
            print("Blender stderr:")
            print(result.stderr.strip())

        return 1

    assert result.data is not None

    print("[OK] Blender process bridge")
    print(
        "       Blender : "
        f"{result.data['blender_version']}"
    )
    print(
        "       Python  : "
        f"{result.data['python_version']}"
    )
    print(
        "       mode    : "
        f"background={result.data['background']}"
    )
    print(
        "       scene   : "
        f"{result.data['scene_name']}"
    )
    print(
        "       result  : "
        f"{result.output_path}"
    )
    print()
    print("Blender runtime probe PASSED.")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="studio2d",
        description=(
            "Studio2D local anime production studio."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Studio2D {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    subparsers.add_parser(
        "doctor",
        help="Check required local production tools.",
    )

    subparsers.add_parser(
        "blender-probe",
        help=(
            "Verify the Studio2D-to-Blender "
            "process bridge."
        ),
    )

    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        return run_doctor()

    if args.command == "blender-probe":
        return run_blender_runtime_probe()

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

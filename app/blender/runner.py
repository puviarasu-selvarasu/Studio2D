"""Controlled Blender process execution for Studio2D."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from shutil import which
import subprocess
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROBE_SCRIPT = (
    PROJECT_ROOT
    / "app"
    / "blender"
    / "scripts"
    / "runtime_probe.py"
)

PROBE_OUTPUT = (
    PROJECT_ROOT
    / "output"
    / "runtime"
    / "blender_probe.json"
)


@dataclass(frozen=True)
class BlenderProbeResult:
    success: bool
    returncode: int | None
    output_path: Path
    data: dict[str, Any] | None
    stdout: str
    stderr: str
    error: str | None


def build_probe_command(
    blender_executable: str,
    script_path: Path = PROBE_SCRIPT,
    output_path: Path = PROBE_OUTPUT,
) -> list[str]:
    return [
        blender_executable,
        "--background",
        "--factory-startup",
        "--python",
        str(script_path),
        "--",
        str(output_path),
    ]


def validate_probe_payload(
    payload: dict[str, Any],
) -> tuple[bool, str | None]:
    required_fields = {
        "schema_version",
        "ok",
        "blender_version",
        "blender_version_tuple",
        "blender_executable",
        "background",
        "python_version",
        "python_executable",
        "scene_name",
    }

    missing = sorted(required_fields - payload.keys())

    if missing:
        return (
            False,
            "Missing probe field(s): " + ", ".join(missing),
        )

    if payload["schema_version"] != 1:
        return False, "Unsupported probe schema version."

    if payload["ok"] is not True:
        return False, "Blender probe did not report success."

    if payload["background"] is not True:
        return False, "Blender did not execute in background mode."

    if not isinstance(payload["blender_version"], str):
        return False, "Invalid Blender version."

    if not isinstance(payload["python_version"], str):
        return False, "Invalid Blender Python version."

    return True, None


def run_blender_probe(
    timeout_seconds: int = 60,
) -> BlenderProbeResult:
    blender_executable = which("blender")

    if blender_executable is None:
        return BlenderProbeResult(
            success=False,
            returncode=None,
            output_path=PROBE_OUTPUT,
            data=None,
            stdout="",
            stderr="",
            error="Blender executable was not found.",
        )

    if not PROBE_SCRIPT.is_file():
        return BlenderProbeResult(
            success=False,
            returncode=None,
            output_path=PROBE_OUTPUT,
            data=None,
            stdout="",
            stderr="",
            error=f"Probe script not found: {PROBE_SCRIPT}",
        )

    PROBE_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if PROBE_OUTPUT.exists():
        PROBE_OUTPUT.unlink()

    command = build_probe_command(
        blender_executable=blender_executable,
    )

    try:
        process = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return BlenderProbeResult(
            success=False,
            returncode=None,
            output_path=PROBE_OUTPUT,
            data=None,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            error=(
                "Blender runtime probe exceeded "
                f"{timeout_seconds} seconds."
            ),
        )
    except OSError as exc:
        return BlenderProbeResult(
            success=False,
            returncode=None,
            output_path=PROBE_OUTPUT,
            data=None,
            stdout="",
            stderr="",
            error=f"Unable to start Blender: {exc}",
        )

    if process.returncode != 0:
        return BlenderProbeResult(
            success=False,
            returncode=process.returncode,
            output_path=PROBE_OUTPUT,
            data=None,
            stdout=process.stdout,
            stderr=process.stderr,
            error=(
                "Blender exited with a non-zero return code."
            ),
        )

    if not PROBE_OUTPUT.is_file():
        return BlenderProbeResult(
            success=False,
            returncode=process.returncode,
            output_path=PROBE_OUTPUT,
            data=None,
            stdout=process.stdout,
            stderr=process.stderr,
            error=(
                "Blender exited successfully but did not "
                "produce the probe JSON."
            ),
        )

    try:
        payload = json.loads(
            PROBE_OUTPUT.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        return BlenderProbeResult(
            success=False,
            returncode=process.returncode,
            output_path=PROBE_OUTPUT,
            data=None,
            stdout=process.stdout,
            stderr=process.stderr,
            error=f"Unable to read Blender probe JSON: {exc}",
        )

    if not isinstance(payload, dict):
        return BlenderProbeResult(
            success=False,
            returncode=process.returncode,
            output_path=PROBE_OUTPUT,
            data=None,
            stdout=process.stdout,
            stderr=process.stderr,
            error="Blender probe payload is not a JSON object.",
        )

    valid, validation_error = validate_probe_payload(
        payload
    )

    return BlenderProbeResult(
        success=valid,
        returncode=process.returncode,
        output_path=PROBE_OUTPUT,
        data=payload,
        stdout=process.stdout,
        stderr=process.stderr,
        error=validation_error,
    )

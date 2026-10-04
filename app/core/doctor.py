"""Runtime tool discovery for Studio2D."""

from __future__ import annotations

from dataclasses import dataclass
from shutil import which
import subprocess
from typing import Sequence


@dataclass(frozen=True)
class ToolSpec:
    name: str
    command: str
    version_args: tuple[str, ...]


@dataclass(frozen=True)
class ToolStatus:
    name: str
    command: str
    found: bool
    path: str | None
    returncode: int | None
    version: str

    @property
    def ok(self) -> bool:
        return self.found and self.returncode == 0


REQUIRED_TOOLS: tuple[ToolSpec, ...] = (
    ToolSpec("Python", "python", ("--version",)),
    ToolSpec("Blender", "blender", ("--version",)),
    ToolSpec("Git", "git", ("--version",)),
    ToolSpec("FFmpeg", "ffmpeg", ("-version",)),
    ToolSpec("Ollama", "ollama", ("--version",)),
)


def _first_nonempty_line(value: str) -> str:
    for line in value.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped

    return "No version output"


def inspect_tool(
    spec: ToolSpec,
    timeout_seconds: int = 20,
) -> ToolStatus:
    executable = which(spec.command)

    if executable is None:
        return ToolStatus(
            name=spec.name,
            command=spec.command,
            found=False,
            path=None,
            returncode=None,
            version="Command not found",
        )

    try:
        result = subprocess.run(
            [executable, *spec.version_args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return ToolStatus(
            name=spec.name,
            command=spec.command,
            found=True,
            path=executable,
            returncode=None,
            version=f"Inspection failed: {exc}",
        )

    combined_output = "\n".join(
        part
        for part in (result.stdout, result.stderr)
        if part
    )

    return ToolStatus(
        name=spec.name,
        command=spec.command,
        found=True,
        path=executable,
        returncode=result.returncode,
        version=_first_nonempty_line(combined_output),
    )


def inspect_required_tools(
    specs: Sequence[ToolSpec] = REQUIRED_TOOLS,
) -> list[ToolStatus]:
    return [inspect_tool(spec) for spec in specs]

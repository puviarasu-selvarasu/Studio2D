"""Studio2D Blender runtime probe.

This file is executed by Blender's bundled Python interpreter.
"""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

import bpy


def get_output_path() -> Path:
    if "--" not in sys.argv:
        raise RuntimeError(
            "Studio2D probe requires an output path after '--'."
        )

    arguments = sys.argv[sys.argv.index("--") + 1 :]

    if len(arguments) != 1:
        raise RuntimeError(
            "Studio2D probe expects exactly one output path."
        )

    return Path(arguments[0]).resolve()


def build_payload() -> dict[str, object]:
    scene = bpy.context.scene

    return {
        "schema_version": 1,
        "ok": True,
        "blender_version": bpy.app.version_string,
        "blender_version_tuple": list(bpy.app.version),
        "blender_executable": bpy.app.binary_path,
        "background": bool(bpy.app.background),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "scene_name": scene.name if scene is not None else None,
    }


def main() -> None:
    output_path = get_output_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = build_payload()

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"STUDIO2D_PROBE_OK: {output_path}")


if __name__ == "__main__":
    main()

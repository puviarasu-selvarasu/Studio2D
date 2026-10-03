from __future__ import annotations

import glob
import shutil
import subprocess
from pathlib import Path


def find_blender() -> str | None:
    found = shutil.which("blender")

    if found:
        return found

    patterns = [
        r"C:\Program Files\Blender Foundation\Blender *\blender.exe",
        r"C:\Program Files\Blender Foundation\*\blender.exe",
    ]

    candidates: list[str] = []

    for pattern in patterns:
        candidates.extend(glob.glob(pattern))

    if not candidates:
        return None

    candidates.sort(reverse=True)

    return candidates[0]


def run_phase1_test() -> int:
    blender = find_blender()

    if blender is None:
        print("Blender not found.")
        return 1

    script = Path(__file__).parent / "scripts" / "phase1_test.py"

    command = [
        blender,
        "--background",
        "--python",
        str(script),
    ]

    print(f"Using Blender: {blender}")
    print("Running Phase 1 Blender automation test...")

    result = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        print(f"Blender exited with code {result.returncode}")
        return result.returncode

    print("Phase 1 Blender automation completed.")
    return 0

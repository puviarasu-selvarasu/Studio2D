from __future__ import annotations

import glob
import platform
import shutil
import subprocess
import sys

from studio2d.blender.runner import run_phase1_test


def run_version(command: list[str]) -> str | None:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        output = (result.stdout or result.stderr).strip()

        if not output:
            return None

        return output.splitlines()[0]

    except (OSError, subprocess.SubprocessError):
        return None


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


def human_memory(total_bytes: int) -> str:
    gb = total_bytes / (1024 ** 3)
    return f"{gb:.1f} GB"


def get_memory() -> str:
    if sys.platform != "win32":
        return "UNKNOWN"

    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)

        ctypes.windll.kernel32.GlobalMemoryStatusEx(
            ctypes.byref(status)
        )

        return human_memory(status.ullTotalPhys)

    except Exception:
        return "UNKNOWN"


def print_item(name: str, status: str, detail: str = "") -> None:
    suffix = f"  {detail}" if detail else ""
    print(f"{name:<14} {status:<10}{suffix}")


def doctor() -> int:
    print()
    print("=" * 62)
    print(" STUDIO2D // SYSTEM DOCTOR")
    print("=" * 62)

    print_item("OS", "INFO", platform.platform())
    print_item("Python", "PASS", sys.version.split()[0])
    print_item("RAM", "INFO", get_memory())

    failures = 0

    blender = find_blender()

    if blender:
        version = run_version([blender, "--version"])
        print_item("Blender", "PASS", version or blender)
        print(f"{'':14} {'':10}Path: {blender}")
    else:
        print_item("Blender", "NOT FOUND")
        failures += 1

    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg:
        version = run_version([ffmpeg, "-version"])
        print_item("FFmpeg", "PASS", version or ffmpeg)
    else:
        print_item("FFmpeg", "NOT FOUND")
        failures += 1

    ollama = shutil.which("ollama")

    if ollama:
        version = run_version([ollama, "--version"])
        print_item("Ollama", "PASS", version or ollama)
    else:
        print_item("Ollama", "NOT FOUND")
        failures += 1

    git = shutil.which("git")

    if git:
        version = run_version([git, "--version"])
        print_item("Git", "PASS", version or git)
    else:
        print_item("Git", "NOT FOUND")
        failures += 1

    print_item(
        "Strategy",
        "INFO",
        "CPU-FIRST / SEQUENTIAL WORKERS",
    )

    print("-" * 62)

    if failures == 0:
        print("STATUS: READY")
        return 0

    print(
        f"STATUS: {failures} REQUIRED TOOL(S) NEED ATTENTION"
    )
    return 1


def main() -> int:
    args = sys.argv[1:]

    if not args:
        print("Studio2D 0.0.1")
        print()
        print("Commands:")
        print("  doctor         Check local Studio2D environment")
        print("  blender-test   Run Blender automation proof")
        return 0

    command = args[0].lower()

    if command == "doctor":
        return doctor()

    if command == "blender-test":
        return run_phase1_test()

    print(f"Unknown command: {command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

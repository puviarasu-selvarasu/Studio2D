"""Tests for the Studio2D Blender process bridge."""

from __future__ import annotations

from pathlib import Path
import unittest

from app.blender.runner import (
    build_probe_command,
    validate_probe_payload,
)


class BlenderRunnerTests(unittest.TestCase):
    def test_probe_command_contract(self) -> None:
        command = build_probe_command(
            blender_executable="blender-test",
            script_path=Path("probe.py"),
            output_path=Path("probe.json"),
        )

        self.assertEqual(
            command,
            [
                "blender-test",
                "--background",
                "--factory-startup",
                "--python",
                "probe.py",
                "--",
                "probe.json",
            ],
        )

    def test_valid_probe_payload(self) -> None:
        payload = {
            "schema_version": 1,
            "ok": True,
            "blender_version": "5.2.0",
            "blender_version_tuple": [5, 2, 0],
            "blender_executable": "blender",
            "background": True,
            "python_version": "3.x",
            "python_executable": "python",
            "scene_name": "Scene",
        }

        valid, error = validate_probe_payload(payload)

        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_probe_requires_background_mode(self) -> None:
        payload = {
            "schema_version": 1,
            "ok": True,
            "blender_version": "5.2.0",
            "blender_version_tuple": [5, 2, 0],
            "blender_executable": "blender",
            "background": False,
            "python_version": "3.x",
            "python_executable": "python",
            "scene_name": "Scene",
        }

        valid, error = validate_probe_payload(payload)

        self.assertFalse(valid)
        self.assertEqual(
            error,
            "Blender did not execute in background mode.",
        )

    def test_probe_rejects_missing_fields(self) -> None:
        valid, error = validate_probe_payload(
            {
                "schema_version": 1,
                "ok": True,
            }
        )

        self.assertFalse(valid)
        self.assertIsNotNone(error)


if __name__ == "__main__":
    unittest.main()

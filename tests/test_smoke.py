"""Smoke tests for the Studio2D foundation."""

from __future__ import annotations

import unittest

from app import __version__
from app.core.doctor import (
    REQUIRED_TOOLS,
    ToolSpec,
    inspect_tool,
)


class Studio2DSmokeTests(unittest.TestCase):
    def test_version_exists(self) -> None:
        self.assertEqual(__version__, "0.1.0")

    def test_required_tool_contract(self) -> None:
        names = {tool.name for tool in REQUIRED_TOOLS}

        self.assertEqual(
            names,
            {
                "Python",
                "Blender",
                "Git",
                "FFmpeg",
                "Ollama",
            },
        )

    def test_python_runtime_can_be_detected(self) -> None:
        status = inspect_tool(
            ToolSpec(
                name="Python",
                command="python",
                version_args=("--version",),
            )
        )

        self.assertTrue(status.found)
        self.assertEqual(status.returncode, 0)
        self.assertIn("Python", status.version)


if __name__ == "__main__":
    unittest.main()

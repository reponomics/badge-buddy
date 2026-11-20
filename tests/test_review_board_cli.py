"""Exercise the board entry point through real files and a stand-in MCP server."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/review_board.py"
FAKE_SERVER = Path(__file__).resolve().parent / "support" / "fake_mcp_server.py"


def run_board(
    directory: Path, *arguments: str, mode: str = ""
) -> subprocess.CompletedProcess:
    """Run the renderer against a configuration that starts the stand-in server."""

    config = directory / "mcp.json"
    config.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "bestpractices": {
                        "command": sys.executable,
                        "args": [str(FAKE_SERVER)],
                        "env": {"FAKE_MCP_MODE": mode},
                    }
                }
            }
        )
    )
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--mcp-config", str(config), *arguments],
        text=True,
        capture_output=True,
        env={**os.environ, "FAKE_MCP_MODE": ""},
    )


class ReviewBoardCliTest(unittest.TestCase):
    def test_all_six_levels_render_without_modifying_input(self):
        with tempfile.TemporaryDirectory(prefix="badge board ") as directory:
            root = Path(directory)
            draft = root / "draft.json"
            original = (
                '{"description_good_status":"Met","OSPS-AC-01.01_status":"Met"}\n'
            )
            draft.write_text(original)
            for level in (
                "passing",
                "silver",
                "gold",
                "baseline-1",
                "baseline-2",
                "baseline-3",
            ):
                with self.subTest(level=level):
                    output = root / f"{level}.html"
                    result = run_board(
                        root,
                        "--input",
                        str(draft),
                        "--output",
                        str(output),
                        "--project-id",
                        "31",
                        "--section",
                        level,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual(
                        output.resolve().as_uri() + "#view=all",
                        json.loads(result.stdout)["url"],
                    )
                    self.assertIn(f'"section":"{level}"', output.read_text())
                    self.assertEqual(original, draft.read_text())

    def test_invalid_input_and_same_destination_fail_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "draft.json"
            for contents, output in (
                ("[]", root / "board.html"),
                ("{}", source),
                ("bad json", root / "board.html"),
            ):
                with self.subTest(contents=contents):
                    source.write_text(contents)
                    result = run_board(
                        root,
                        "--input",
                        str(source),
                        "--output",
                        str(output),
                        "--project-id",
                        "31",
                        "--section",
                        "baseline-1",
                    )
                    self.assertEqual(1, result.returncode)
                    self.assertEqual(contents, source.read_text())
                    if output != source:
                        self.assertFalse(output.exists())

    def test_project_mismatch_does_not_create_or_replace_board(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "draft.json"
            source.write_text('{"id": 32, "description_good_status": "Met"}')
            output = root / "board.html"
            for existing in (False, True):
                if existing:
                    output.write_text("previous preview")
                result = run_board(
                    root,
                    "--input",
                    str(source),
                    "--output",
                    str(output),
                    "--project-id",
                    "31",
                    "--section",
                    "passing",
                )
                self.assertEqual(1, result.returncode)
                self.assertIn("does not match", result.stderr)
                if existing:
                    self.assertEqual("previous preview", output.read_text())
                else:
                    self.assertFalse(output.exists())

    def test_matching_numeric_id_and_local_label_can_render(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "draft.json"
            source.write_text('{"id": 31}')
            for selected in ("31", "Local draft"):
                result = run_board(
                    root,
                    "--input",
                    str(source),
                    "--output",
                    str(root / "board.html"),
                    "--project-id",
                    selected,
                    "--section",
                    "passing",
                )
                self.assertEqual(0, result.returncode, result.stderr)

    def test_criteria_come_from_the_configured_server(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "draft.json").write_text('{"dco_status": "Unmet"}')
            output = root / "board.html"
            result = run_board(
                root,
                "--input",
                str(root / "draft.json"),
                "--output",
                str(output),
                "--project-id",
                "31",
                "--section",
                "silver",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            markup = output.read_text()
            self.assertIn("The project SHOULD do what dco describes.", markup)
            self.assertIn('"dco":{"status":"Unmet"', markup)

    def test_unavailable_criteria_fail_without_creating_or_replacing_a_board(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "draft.json").write_text("{}")
            output = root / "board.html"
            for existing in (False, True):
                if existing:
                    output.write_text("previous preview")
                result = run_board(
                    root,
                    "--input",
                    str(root / "draft.json"),
                    "--output",
                    str(output),
                    "--project-id",
                    "31",
                    "--section",
                    "passing",
                    mode="tool_error",
                )
                self.assertEqual(1, result.returncode)
                if existing:
                    self.assertEqual("previous preview", output.read_text())
                else:
                    self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

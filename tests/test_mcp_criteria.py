"""The board's MCP client against a stand-in stdio server."""

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "support"))

from criteria_records import RECORDS  # noqa: E402
from ossf_review.mcp_criteria import (  # noqa: E402
    DEFAULT_CONFIG,
    CriteriaUnavailable,
    _stop_server,
    fetch_criteria,
    server_command,
)

FAKE_SERVER = Path(__file__).resolve().parent / "support" / "fake_mcp_server.py"
FAKE_LAUNCHER = FAKE_SERVER.with_name("fake_mcp_launcher.py")


class McpCriteriaTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.config = Path(directory.name) / "mcp.json"

    def register(self, mode="", command=sys.executable, args=None):
        server = {
            "command": command,
            "args": [str(FAKE_SERVER)] if args is None else args,
            "env": {"FAKE_MCP_MODE": mode},
        }
        self.config.write_text(json.dumps({"mcpServers": {"bestpractices": server}}))

    def test_returns_the_levels_records_in_server_order(self):
        for mode in ("", "text_only"):
            with self.subTest(mode=mode):
                self.register(mode)
                self.assertEqual(
                    RECORDS["baseline-2"],
                    fetch_criteria("baseline-2", config_path=self.config),
                )

    def test_failures_are_reported_as_unavailable_criteria(self):
        # The last value is text the server itself emits, which the error must carry.
        cases = (
            ("tool_error", sys.executable, None, "No such level."),
            ("exit", sys.executable, None, ""),
            (
                "",
                sys.executable,
                ["-c", "import sys; sys.exit('resolver said no')"],
                "resolver said no",
            ),
            ("", str(self.config.parent / "missing-executable"), None, ""),
        )
        for mode, command, args, server_text in cases:
            with self.subTest(mode=mode, command=command, args=args):
                self.register(mode, command, args)
                with self.assertRaises(CriteriaUnavailable) as raised:
                    fetch_criteria("passing", config_path=self.config)
                self.assertIn(server_text, str(raised.exception))

    def test_stalled_server_is_stopped_at_the_timeout(self):
        self.register("stall")
        started = time.monotonic()
        with self.assertRaises(CriteriaUnavailable):
            fetch_criteria("passing", config_path=self.config, timeout=0.5)
        self.assertLess(time.monotonic() - started, 10)

    @unittest.skipUnless(os.name == "posix", "POSIX process-group cleanup")
    def test_timeout_stops_launcher_and_child_holding_the_pipe(self):
        self.assert_launcher_stopped("stall")

    @unittest.skipUnless(os.name == "posix", "POSIX process-group cleanup")
    def test_protocol_failure_stops_the_launched_child(self):
        self.assert_launcher_stopped("invalid_json")

    @unittest.skipUnless(os.name == "posix", "POSIX process-group cleanup")
    def test_timeout_cleans_up_once_after_the_launcher_has_exited(self):
        with patch("ossf_review.mcp_criteria._stop_server", wraps=_stop_server) as stop:
            error = self.assert_launcher_stopped("launcher_exit")
        self.assertIn("the server stopped before answering", error)
        self.assertEqual(1, stop.call_count)

    def assert_launcher_stopped(self, mode):
        survivor = self.config.parent / "survivor.txt"
        self.register(mode, args=[str(FAKE_LAUNCHER), str(survivor)])
        started = time.monotonic()
        with self.assertRaises(CriteriaUnavailable) as raised:
            fetch_criteria("passing", config_path=self.config, timeout=0.5)
        elapsed = time.monotonic() - started
        self.assertTrue(survivor.with_suffix(".started").exists())
        # A surviving child writes after two seconds, including when a protocol
        # failure made the client return promptly. The fixture exits by itself.
        time.sleep(max(0, started + 2.5 - time.monotonic()))
        self.assertLess(elapsed, 1.5, "a descendant kept the MCP pipe open")
        self.assertFalse(survivor.exists(), "the launched child survived cleanup")
        return str(raised.exception)

    def test_configuration_must_register_the_server(self):
        for contents in (
            "{}",
            '{"mcpServers": {"other": {"command": "x"}}}',
            "not json",
            '{"mcpServers": {"bestpractices": {"command": 3}}}',
        ):
            with self.subTest(contents=contents):
                self.config.write_text(contents)
                with self.assertRaises(CriteriaUnavailable):
                    server_command(self.config)
        with self.assertRaises(CriteriaUnavailable):
            server_command(self.config.parent / "absent.json")

    def test_default_is_the_plugins_own_registration_and_is_usable(self):
        self.assertEqual(ROOT / ".mcp.json", DEFAULT_CONFIG)
        server_command(DEFAULT_CONFIG)


if __name__ == "__main__":
    unittest.main()

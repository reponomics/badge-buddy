"""The plugin against the real, pinned MCP server.

These tests start the server registered in ``.mcp.json``, which downloads it on first
use, so they run from ``make test-live`` and not with the offline suite.
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from support.stdio_client import server_session

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from ossf_review import mcp_criteria  # noqa: E402
from ossf_review.criteria import SECTION_NAMES  # noqa: E402

SKILL = ROOT / "skills" / "ossf-bp-badges" / "SKILL.md"
TOOL_PREFIX = "mcp__plugin_badge-buddy_bestpractices__"


def server_tools() -> set[str]:
    """Ask the pinned server which tools it offers."""

    command, environment = mcp_criteria.server_command()
    with tempfile.TemporaryDirectory() as directory:
        environment["BESTPRACTICES_DATA_DIR"] = directory
        with server_session(command, environment=environment) as server:
            tools = server.request("tools/list")["tools"]
    return {tool["name"] for tool in tools}


class PinnedServerContractTest(unittest.TestCase):
    def test_every_tool_the_skill_is_allowed_to_call_exists(self) -> None:
        frontmatter = SKILL.read_text(encoding="utf-8").split("---", 2)[1]
        allowed = set(re.findall(rf"{TOOL_PREFIX}(\w+)", frontmatter))
        self.assertTrue(allowed, "the skill pre-allows no MCP tools")
        self.assertEqual(set(), allowed - server_tools())

    def test_every_tool_the_application_guide_calls_exists(self) -> None:
        guide = (SKILL.parent / "references" / "application.md").read_text(
            encoding="utf-8"
        )
        # The guide writes calls as `tool_name(arguments)`; anything in that form must be a tool.
        called = set(re.findall(r"`([a-z_]+)\(", guide))
        self.assertTrue(called, "the guide names no tool calls")
        self.assertEqual(set(), called - server_tools())

    def test_the_board_renders_every_level_from_the_servers_criteria(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.json"
            draft.write_text("{}")
            for level in SECTION_NAMES:
                with self.subTest(level=level):
                    output = Path(directory) / f"{level}.html"
                    arguments = ["--input", str(draft), "--output", str(output)]
                    arguments += ["--project-id", "1", "--section", level]
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(ROOT / "scripts" / "review_board.py"),
                            *arguments,
                        ],
                        text=True,
                        capture_output=True,
                        timeout=90,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    payload = re.search(
                        r'id="assessment-data"[^>]*>(.*?)</script>',
                        output.read_text(),
                        re.S,
                    )
                    self.assertGreater(json.loads(payload.group(1))["total"], 0)


class DraftWorkflowContractTest(unittest.TestCase):
    """Exercise the skill's tool contracts, not an agent following the skill.

    The production package/stdio/schema/handlers run unchanged. Its public factory
    receives synthetic BadgeApp responses and a temporary draft root. No call reaches
    the public site, authenticates, or reads the user's draft storage.
    """

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        command, environment = mcp_criteria.server_command()
        self.requirement = command[2]
        fixture = Path(__file__).parent / "support" / "fixture_server.py"
        command = [*command[:-1], "python", "-I", str(fixture), str(self.root)]
        self.server = self.enterContext(
            server_session(command, environment=environment)
        )
        self.assertEqual(
            self.requirement.split("==")[1],
            self.server.initialize["serverInfo"]["version"],
        )

    def read(self, project_id=123):
        return self.server.call("read_draft", {"project_id": project_id})

    def update(self, changes):
        return self.server.call("update_draft", {"project_id": 123, "changes": changes})

    def test_draft_lifecycle_and_rejected_patch_preserve_saved_work(self):
        self.server.call("read_draft", {"project_id": 123}, error="draft_not_found")
        initial = self.server.call(
            "build_draft",
            {"draft": {}, "changes": {"contribution_status": "Met"}},
        )["draft"]
        self.assertFalse((self.root / "drafts").exists())
        saved = self.update(initial)
        location = Path(saved["location"])
        self.assertTrue(location.is_relative_to(self.root))
        before = location.read_bytes()
        finding = self.server.call(
            "validate_draft", {"project_id": 123, "section": "passing"}
        )
        self.assertIn(
            "missing_required_url", {item["code"] for item in finding["findings"]}
        )
        for changes in (
            {"contribution_status": "Unmet", "unknown_patch_field": "value"},
            {"contribution_status": "Unmet", "contribution_justification": 17},
            {"contribution_status": "invalid"},
        ):
            with self.subTest(changes=changes):
                self.server.call(
                    "update_draft",
                    {"project_id": 123, "changes": changes},
                    error="invalid_field",
                )
                self.assertEqual(before, location.read_bytes())
                self.assertEqual(initial, self.read()["draft"])
        wording = "See https://example.org/fixture/contributing."
        self.update({"contribution_justification": wording})
        self.assertEqual("Met", self.read()["draft"]["contribution_status"])
        checked = self.server.call(
            "validate_draft", {"project_id": 123, "section": "passing"}
        )
        self.assertEqual([], checked["findings"])
        self.update({"contribution_justification": None})
        self.assertEqual(initial, self.read()["draft"])
        self.server.call("read_draft", {"project_id": 456}, error="draft_not_found")
        self.assertFalse((self.root / "requests.jsonl").exists())

    def test_saved_answers_and_explicit_delta_proposal_leave_both_sources_unchanged(
        self,
    ):
        found = self.server.call(
            "find_project", {"query": "https://example.org/fixture"}
        )
        self.assertEqual(123, found["candidates"][0]["project"]["project_id"])
        status = self.server.call("get_project_status", {"project_id": 123})
        self.assertEqual("in_progress", status["badge_level"])
        arguments = {
            "project_id": 123,
            "level": "passing",
            "statuses": ["Met", "Unmet", "N/A"],
        }
        saved = self.server.call("get_project_answers", arguments)["answers"]
        self.assertEqual("Met", saved["contribution_status"])
        self.update(saved)
        revised = "The fixture now documents a more specific purpose."
        self.update({"description_good_justification": revised})
        stored = self.read()["draft"]
        # Selection of differences is the caller's policy; MCP must honor this
        # explicit subset rather than merge unrelated stored answers into it.
        delta = {
            "description_good_status": "Met",
            "description_good_justification": revised,
        }
        proposal = self.server.call(
            "prepare_update_url",
            {
                "project_id": 123,
                "section": "passing",
                "draft": delta,
                "overrides": {
                    "mode": "fields",
                    "fields": ["description_good_justification"],
                },
            },
        )
        url = urlsplit(proposal["artifact"]["url"])
        self.assertEqual("/en/projects/123/passing/edit", url.path)
        self.assertEqual(
            {
                **{key: [value] for key, value in delta.items()},
                "overrides": ["description_good_justification"],
            },
            parse_qs(url.query),
        )
        self.assertEqual(
            ["description_good_justification"], proposal["effective_overrides"]
        )
        self.assertEqual(stored, self.read()["draft"])
        self.assertEqual(
            saved, self.server.call("get_project_answers", arguments)["answers"]
        )
        requests = [
            json.loads(line)
            for line in (self.root / "requests.jsonl").read_text().splitlines()
        ]
        self.assertTrue(requests)
        self.assertEqual({"GET"}, {item["method"] for item in requests})

    def test_explicit_validation_does_not_create_or_replace_a_stored_draft(self):
        arguments = {"project_id": 123, "section": "passing"}
        invalid = {"description_good_status": "N/A"}
        result = self.server.call("validate_draft", {**arguments, "draft": invalid})
        self.assertIn("na_not_allowed", {item["code"] for item in result["findings"]})
        self.assertFalse((self.root / "drafts").exists())
        self.update({"description_good_status": "Met"})
        self.server.call("validate_draft", {**arguments, "draft": invalid})
        self.assertEqual({"description_good_status": "Met"}, self.read()["draft"])
        self.server.call(
            "prepare_update_url",
            {**arguments, "draft": {"id": 456}},
            error="project_mismatch",
        )
        self.assertEqual({"description_good_status": "Met"}, self.read()["draft"])

    def test_unknown_reset_and_large_proposal_report_their_transfer_limits(self):
        arguments = {"project_id": 123, "section": "passing"}
        unknown = self.server.call(
            "prepare_update_url",
            {
                **arguments,
                "draft": {"description_good_status": "?"},
                "overrides": {"mode": "all"},
            },
        )
        self.assertIn(
            "unknown_status_reset_unsupported",
            {item["code"] for item in unknown["warnings"]},
        )
        # The server warns rather than enforcing the plugin's manual-reset policy.
        self.assertFalse((self.root / "drafts").exists())
        wording = "A long explanation: " + "Ω" * 1500
        large = self.server.call(
            "prepare_update_url",
            {
                **arguments,
                "draft": {
                    "description_good_status": "Met",
                    "description_good_justification": wording,
                },
            },
        )
        artifact = large["artifact"]
        self.assertEqual(
            len(artifact["url"].encode("utf-8")), artifact["encoded_size_bytes"]
        )
        self.assertGreater(artifact["encoded_size_bytes"], 6000)
        self.assertEqual(
            [wording],
            parse_qs(urlsplit(artifact["url"]).query)["description_good_justification"],
        )
        self.assertFalse((self.root / "drafts").exists())


if __name__ == "__main__":
    unittest.main()

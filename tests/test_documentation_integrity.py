"""Check local document references and CLI example syntax, not agent behavior."""

from __future__ import annotations

import json
import shlex
import sys
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = PLUGIN_ROOT / "skills"


class DocumentationIntegrityTest(unittest.TestCase):
    def test_raw_references_do_not_require_claude_substitution(self) -> None:
        for path in SKILLS_ROOT.glob("*/references/**/*.md"):
            with self.subTest(path=str(path.relative_to(SKILLS_ROOT))):
                self.assertNotRegex(path.read_text(), r"\$\{CLAUDE_[A-Z_]+\}")

    def test_skill_permission_rules_have_no_command_template_placeholders(self) -> None:
        for path in SKILLS_ROOT.glob("*/SKILL.md"):
            frontmatter = path.read_text().split("---", 2)[1]
            with self.subTest(path=path.parent.name):
                self.assertNotIn("<controller-path>", frontmatter)
                self.assertNotIn("<scorecard-controller>", frontmatter)

    def test_scorecard_documented_commands_parse(self) -> None:
        # Parse the examples without executing commands or making requests.
        scripts = str(PLUGIN_ROOT / "scripts")
        sys.path.insert(0, scripts)
        self.addCleanup(sys.path.remove, scripts)
        import scorecard

        parser = scorecard.build_parser()
        examples = []
        for path in sorted((SKILLS_ROOT / "ossf-scorecard").rglob("*.md")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith('"<scorecard-controller>" '):
                    examples.append((path, line))
        self.assertTrue(examples, "No Scorecard command examples found")
        for path, line in examples:
            with self.subTest(path=path.name, command=line):
                parser.parse_args(shlex.split(line)[1:])

    def test_registered_mcp_is_pinned_and_uses_stdio(self) -> None:
        config = json.loads((PLUGIN_ROOT / ".mcp.json").read_text())
        server = config["mcpServers"]["bestpractices"]
        self.assertEqual("uvx", server["command"])
        flag, requirement, executable = server["args"]
        self.assertEqual(("--from", "bestpractices-mcp"), (flag, executable))
        # Policy: the server is pinned to one exact release, never a range or latest.
        self.assertRegex(requirement, r"^best-practices-mcp==\d+\.\d+\.\d+$")
        # Policy: the dependency list that is monitored for vulnerabilities names the
        # version that actually runs.
        listed = (PLUGIN_ROOT / "requirements-mcp.txt").read_text().splitlines()
        self.assertIn(requirement, listed)
        # Policy: drafts stay in the server's default location, shared with other hosts.
        self.assertNotIn("env", server)

    def test_scorecard_registration_uses_one_overridable_executable(self) -> None:
        config = json.loads((PLUGIN_ROOT / ".mcp.json").read_text())
        server = config["mcpServers"]["scorecard"]
        # Use the installed upstream binary directly; expansion is the host's
        # supported command-field mechanism, not a shell or download wrapper.
        self.assertEqual("${BADGE_BUDDY_SCORECARD_BIN:-scorecard}", server["command"])
        self.assertEqual(["mcp"], server["args"])
        self.assertNotIn("env", server)

    def test_scorecard_permissions_name_only_the_supported_mcp_tools(self) -> None:
        frontmatter = (
            (SKILLS_ROOT / "ossf-scorecard/SKILL.md").read_text().split("---", 2)[1]
        )
        rules = next(
            line.removeprefix("allowed-tools: ").split(", ")
            for line in frontmatter.splitlines()
            if line.startswith("allowed-tools:")
        )
        mcp_rules = {rule for rule in rules if rule.startswith("mcp__")}
        expected = {
            "get_repo_score",
            "get_check_result",
            "compare_repos",
            "list_checks",
            "explain_check",
        }
        self.assertEqual(
            {f"mcp__plugin_badge-buddy_scorecard__{tool}" for tool in expected},
            mcp_rules,
        )
        # A machine-specific CLI path must not require arbitrary Bash access.
        shell_rules = {rule for rule in rules if rule.startswith("Bash")}
        self.assertEqual(
            {
                'Bash("${CLAUDE_PLUGIN_ROOT}/scripts/scorecard.py" *)',
                "Bash(${CLAUDE_PLUGIN_ROOT}/scripts/scorecard.py *)",
            },
            shell_rules,
        )

    def test_board_documented_command_parses(self) -> None:
        scripts = str(PLUGIN_ROOT / "scripts")
        sys.path.insert(0, scripts)
        self.addCleanup(sys.path.remove, scripts)
        import review_board

        guide = SKILLS_ROOT / "ossf-bp-badges/references/application.md"
        example = next(
            line
            for line in guide.read_text().splitlines()
            if line.startswith('python3 "<board-renderer>"')
        )
        args = review_board.build_parser().parse_args(shlex.split(example)[2:])
        self.assertEqual("baseline-1", args.section)
        self.assertEqual("all", args.view)


if __name__ == "__main__":
    unittest.main()

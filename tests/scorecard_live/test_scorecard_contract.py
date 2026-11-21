"""Real installed Scorecard contracts, separate from the offline unit suite.

MCP queries use only a loopback REST fixture. CLI scans use disposable local
files, without repository credentials or public scores. Run with
``make test-scorecard SCORECARD=/absolute/path/to/scorecard``.
"""

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests" / "live"))

from support.stdio_client import server_session  # noqa: E402

BASELINE = json.loads((ROOT / ".github" / "ci" / "scorecard.json").read_text())
COMMIT = "a" * 40
ENVIRONMENT = dict.fromkeys(
    (
        "GITHUB_AUTH_TOKEN",
        "GITHUB_TOKEN",
        "GH_AUTH_TOKEN",
        "GH_TOKEN",
        "GITLAB_AUTH_TOKEN",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ),
    "",
)


def published_result():
    """An intentionally partial historical report, richer than MCP summaries."""
    return {
        "repo": {"name": "github.com/example/project", "commit": COMMIT},
        "scorecard": {"version": "v5.6.0", "commit": "b" * 40},
        "date": "2026-10-01T00:00:00Z",
        "score": 4.5,
        "future_field": {"preserve_in_original": True},
        "checks": [
            {
                "name": "Pinned-Dependencies",
                "score": 0,
                "reason": "fixture unpinned dependencies",
                "details": [f"fixture detail {index}" for index in range(505)],
                "annotations": ["fixture maintainer context"],
                "documentation": {
                    "short": "Fixture documentation",
                    "url": "https://example.invalid/check",
                },
            },
            {"name": "Signed-Releases", "score": -1, "reason": "fixture unavailable"},
        ],
    }


class ScorecardCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.executable = shutil.which(os.environ.get("SCORECARD", "scorecard"))
        if not cls.executable:
            raise AssertionError(
                "Install Scorecard v5.7.0 or set SCORECARD to its path"
            )
        result = subprocess.run(
            [cls.executable, "version", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        cls.identity = json.loads(result.stdout)
        if cls.identity["gitVersion"] != BASELINE["version"]:
            raise AssertionError(f"Untested Scorecard version: {cls.identity}")
        if cls.identity["gitCommit"] != BASELINE["commit"]:
            raise AssertionError(f"Unexpected Scorecard build: {cls.identity}")
        print(f"Scorecard contract build: {cls.executable} {cls.identity}")


class MCPContractTest(ScorecardCase):
    def setUp(self):
        self.requests = []
        requests = self.requests
        self.results = {COMMIT: published_result()}
        results = self.results

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append((self.path, dict(self.headers)))
                url = urlsplit(self.path)
                name = url.path.rsplit("/", 1)[-1]
                commit = parse_qs(url.query).get("commit", [COMMIT])[0]
                status = {"missing": 404, "unavailable": 503}.get(name, 200)
                body = (
                    b"not JSON"
                    if name == "malformed"
                    else json.dumps(results.get(commit, results[COMMIT])).encode()
                )
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, _format, *_args):
                pass

        http = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=http.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(http.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(http.shutdown)
        self.server = self.enterContext(
            server_session(
                [
                    self.executable,
                    "mcp",
                    f"--base-url=http://127.0.0.1:{http.server_port}",
                ],
                environment=ENVIRONMENT,
                timeout=30,
            )
        )

    def error(self, name, arguments):
        result = self.server.request(
            "tools/call", {"name": name, "arguments": arguments}
        )
        self.assertTrue(result.get("isError"), result)
        return " ".join(block.get("text", "") for block in result["content"])

    def test_advertised_tools_and_skill_permissions(self):
        tools = {
            tool["name"]: tool for tool in self.server.request("tools/list")["tools"]
        }
        expected = {
            "get_repo_score",
            "get_check_result",
            "compare_repos",
            "list_checks",
            "explain_check",
        }
        self.assertEqual(expected, set(tools))
        self.assertEqual(
            BASELINE["version"], self.server.initialize["serverInfo"]["version"]
        )
        frontmatter = (
            (ROOT / "skills/ossf-scorecard/SKILL.md").read_text().split("---", 2)[1]
        )
        allowed = set(
            re.findall(r"mcp__plugin_badge-buddy_scorecard__(\w+)", frontmatter)
        )
        self.assertTrue(allowed, "Scorecard skill must declare actual MCP permissions")
        self.assertEqual(set(), allowed - expected)
        for tool in tools.values():
            self.assertTrue(tool["annotations"]["readOnlyHint"])
            self.assertIn("inputSchema", tool)
            self.assertIn("outputSchema", tool)

    def test_catalog_and_explanation_are_offline_and_versioned(self):
        catalog = self.server.call("list_checks", {})
        self.assertEqual(BASELINE["version"], catalog["scorecard_version"])
        self.assertIn("Fuzzing", {check["name"] for check in catalog["checks"]})
        explanation = self.server.call("explain_check", {"check": "fuzzing"})
        self.assertEqual("Fuzzing", explanation["check"]["name"])
        self.assertTrue(explanation["check"]["description"])
        self.assertIn(BASELINE["commit"], explanation["check"]["documentation_url"])
        self.assertIn(
            "unknown check", self.error("explain_check", {"check": "Imaginary"})
        )
        self.assertEqual([], self.requests)

    def test_published_identity_partial_coverage_and_zero_are_preserved(self):
        result = self.server.call(
            "get_repo_score", {"repo": "example/project", "commit": COMMIT}
        )
        self.assertEqual(COMMIT, result["commit"])
        self.assertEqual("v5.6.0", result["scorecard"]["version"])
        self.assertEqual("b" * 40, result["scorecard"]["commit"])
        self.assertNotEqual(result["commit"], result["scorecard"]["commit"])
        self.assertEqual("2026-10-01T00:00:00Z", result["date"])
        self.assertEqual("cached-rest", result["source"])
        self.assertTrue(result["caveats"])
        self.assertEqual(4.5, result["score"])
        self.assertFalse(result["complete"])
        self.assertIn("License", result["missing_checks"])
        self.assertEqual(
            {"Pinned-Dependencies": 0, "Signed-Releases": -1},
            {c["name"]: c["score"] for c in result["checks"]},
        )
        self.assertNotIn("future_field", result)
        self.assertNotIn("details", result["checks"][0])
        self.assertNotIn("documentation", result["checks"][0])
        path, headers = self.requests[0]
        self.assertEqual(f"/projects/github.com/example/project?commit={COMMIT}", path)
        self.assertNotIn("Authorization", headers)

    def test_detail_caps_report_truncation_and_are_not_lossless_exports(self):
        for requested, count in ((None, 50), (2, 2), (500, 500), (999, 500)):
            with self.subTest(max_details=requested):
                arguments = {"repo": "example/project", "check": "Pinned-Dependencies"}
                if requested is not None:
                    arguments["max_details"] = requested
                result = self.server.call("get_check_result", arguments)["check"]
                self.assertEqual(count, len(result["details"]))
                self.assertEqual(505, result["details_total"])
                self.assertTrue(result["details_truncated"])
                self.assertNotIn("annotations", result)

    def test_check_detail_has_no_aggregate_and_omits_empty_optional_fields(self):
        result = self.server.call(
            "get_check_result", {"repo": "example/project", "check": "Signed-Releases"}
        )
        self.assertNotIn("score", result)
        self.assertEqual(-1, result["check"]["score"])
        self.assertEqual(0, result["check"]["details_total"])
        self.assertFalse(result["check"]["details_truncated"])
        self.assertNotIn("details", result["check"])
        self.assertNotIn("documentation", result["check"])
        detailed = self.server.call(
            "get_check_result",
            {"repo": "example/project", "check": "Pinned-Dependencies"},
        )
        self.assertEqual(
            self.results[COMMIT]["checks"][0]["documentation"],
            detailed["check"]["documentation"],
        )

    def test_historical_commits_keep_their_own_details_and_scanner_context(self):
        newer_commit = "d" * 40
        newer = published_result()
        newer["repo"]["commit"] = newer_commit
        newer["scorecard"] = {
            "version": BASELINE["version"],
            "commit": BASELINE["commit"],
        }
        newer["date"] = "2026-11-01T00:00:00Z"
        newer["checks"][1]["score"] = 8
        newer["checks"][1]["reason"] = "fixture newly conclusive"
        newer["checks"].append(
            {"name": "License", "score": 10, "reason": "fixture license"}
        )
        self.results[newer_commit] = newer
        observations = []
        for commit in (COMMIT, newer_commit):
            overview = self.server.call(
                "get_repo_score", {"repo": "example/project", "commit": commit}
            )
            detail = self.server.call(
                "get_check_result",
                {
                    "repo": "example/project",
                    "commit": commit,
                    "check": "Signed-Releases",
                },
            )
            self.assertEqual(commit, overview["commit"])
            self.assertEqual(commit, detail["commit"])
            self.assertEqual(overview["scorecard"], detail["scorecard"])
            observations.append((overview, detail))
        before, after = observations
        self.assertEqual(-1, before[1]["check"]["score"])
        self.assertEqual(8, after[1]["check"]["score"])
        self.assertIn("License", before[0]["missing_checks"])
        self.assertNotIn("License", after[0]["missing_checks"])
        self.assertNotEqual(before[0]["scorecard"], after[0]["scorecard"])
        self.assertEqual(
            [
                f"/projects/github.com/example/project?commit={commit}"
                for commit in (COMMIT, COMMIT, newer_commit, newer_commit)
            ],
            [path for path, _ in self.requests],
        )

    def test_complete_means_catalog_coverage_not_conclusive_or_untruncated(self):
        catalog = self.server.call("list_checks", {})
        expected = {
            check["name"]
            for check in catalog["checks"]
            if not check.get("experimental")
            and "github"
            in [platform.lower() for platform in check["supported_platforms"]]
        }
        self.assertIn("License", expected)
        report = self.results[COMMIT]
        present = {check["name"] for check in report["checks"]}
        report["checks"].extend(
            {"name": name, "score": -1, "reason": "fixture unavailable"}
            for name in sorted(expected - present)
        )
        overview = self.server.call("get_repo_score", {"repo": "example/project"})
        self.assertTrue(overview["complete"])
        self.assertFalse(overview.get("missing_checks"))
        self.assertEqual("v5.6.0", overview["scorecard"]["version"])
        self.assertIn(-1, [check["score"] for check in overview["checks"]])
        detail = self.server.call(
            "get_check_result",
            {"repo": "example/project", "check": "Pinned-Dependencies"},
        )
        self.assertTrue(detail["complete"])
        self.assertTrue(detail["check"]["details_truncated"])

    def test_missing_check_and_acquisition_failures_are_distinct(self):
        missing = self.error(
            "get_check_result", {"repo": "example/project", "check": "License"}
        )
        self.assertIn("missing", missing.lower())
        for repo, expected in (
            ("missing", "no published"),
            ("unavailable", "503"),
            ("malformed", "decoding"),
        ):
            with self.subTest(repo=repo):
                self.assertIn(
                    expected,
                    self.error("get_repo_score", {"repo": f"example/{repo}"}).lower(),
                )

    def test_pinned_commit_mismatch_and_subgroups_are_rejected(self):
        mismatch = self.error(
            "get_repo_score", {"repo": "example/project", "commit": "c" * 40}
        )
        self.assertIn("different commit", mismatch)
        self.requests.clear()
        subgroup = self.error(
            "get_repo_score", {"repo": "gitlab.com/group/subgroup/project"}
        )
        self.assertIn("subgroup paths are not supported", subgroup)
        self.assertEqual([], self.requests)

    def test_comparison_preserves_per_repository_errors(self):
        result = self.server.call(
            "compare_repos", {"repos": ["example/project", "example/missing"]}
        )
        self.assertFalse(result["truncated"])
        self.assertEqual(2, len(result["results"]))
        self.assertEqual(4.5, result["results"][0]["score"])
        self.assertIn("no published", result["results"][1]["error"].lower())
        self.assertNotIn("score", result["results"][1])


class CLIContractTest(ScorecardCase):
    def setUp(self):
        self.directory = self.enterContext(tempfile.TemporaryDirectory())
        self.root = Path(self.directory).resolve()
        self.repo = self.root / "repository"
        self.repo.mkdir()
        (self.repo / "LICENSE").write_text("MIT License\n", encoding="utf-8")
        (self.repo / "scorecard.yml").write_text(
            "annotations:\n  - checks: [license]\n    reasons:\n      - reason: test-data\n",
            encoding="utf-8",
        )

    def scan(self, checks, output):
        self.assertFalse(
            output.exists(), "Each measurement must use a fresh destination"
        )
        return subprocess.run(
            [
                self.executable,
                f"--local={self.repo}",
                f"--checks={checks}",
                "--format=json",
                "--show-details",
                "--show-annotations",
                "--verbosity=debug",
                f"--output={output}",
            ],
            text=True,
            capture_output=True,
            env={**os.environ, **ENVIRONMENT},
            timeout=30,
        )

    def test_local_json_retains_details_annotations_and_identity(self):
        output = self.root / "local.json"
        scan = self.scan("License", output)
        self.assertEqual(0, scan.returncode, scan.stderr)
        raw = json.loads(output.read_text())
        self.assertTrue(raw["repo"]["name"].startswith("file://"))
        self.assertIsInstance(raw["score"], (int, float))
        self.assertTrue(raw["checks"][0]["documentation"]["url"])
        self.assertEqual(BASELINE["version"], raw["scorecard"]["version"])
        self.assertEqual(BASELINE["commit"], raw["scorecard"]["commit"])
        self.assertTrue(raw["checks"][0]["details"])
        self.assertTrue(raw["checks"][0]["annotations"])
        self.assertEqual(["License"], [check["name"] for check in raw["checks"]])
        self.assertGreaterEqual(raw["checks"][0]["score"], 0)

    def test_local_fuzzing_recognizes_a_python_fixture_without_running_it(self):
        (self.repo / "fuzz.py").write_text("import atheris\n", encoding="utf-8")
        output = self.root / "fuzzing.json"
        scan = self.scan("Fuzzing", output)
        self.assertEqual(0, scan.returncode, scan.stderr)
        checks = json.loads(output.read_text())["checks"]
        self.assertEqual(["Fuzzing"], [check["name"] for check in checks])
        self.assertGreater(checks[0]["score"], 0)
        # This validates detector recognition only, not target quality or execution.

    def test_nonzero_exit_still_preserves_useful_partial_results(self):
        workflows = self.repo / ".github/workflows"
        workflows.mkdir(parents=True)
        (workflows / "broken.yml").write_text("jobs: [unclosed\n", encoding="utf-8")
        output = self.root / "partial.json"
        scan = self.scan("License,Token-Permissions", output)
        self.assertNotEqual(0, scan.returncode)
        self.assertIn("Token-Permissions", scan.stderr)
        raw = json.loads(output.read_text())
        self.assertEqual(
            {"License", "Token-Permissions"}, {check["name"] for check in raw["checks"]}
        )
        checks = {check["name"]: check for check in raw["checks"]}
        self.assertGreaterEqual(checks["License"]["score"], 0)
        self.assertEqual(-1, checks["Token-Permissions"]["score"])
        self.assertIn("invalid GitHub workflow", checks["Token-Permissions"]["reason"])

    def test_documented_local_command_preserves_failure_under_errexit(self):
        workflows = self.repo / ".github/workflows"
        workflows.mkdir(parents=True)
        (workflows / "broken.yml").write_text("jobs: [unclosed\n", encoding="utf-8")
        reference = (
            ROOT / "skills/ossf-scorecard/references/authentication-and-results.md"
        ).read_text()
        blocks = re.findall(r"```bash\n(.*?)```", reference, re.DOTALL)
        command = next(block for block in blocks if "--local=" in block)
        command = command.replace(
            '"<scorecard-executable>"', shlex.quote(self.executable)
        )
        command = command.replace(
            '"/absolute/path/to/project"', shlex.quote(str(self.repo))
        )
        command = command.replace(
            "--checks=Fuzzing", "--checks=License,Token-Permissions"
        )
        command = command.replace(
            "mktemp -d",
            "mktemp -d " + shlex.quote(str(self.root / "diagnostic.XXXXXX")),
        )
        result = subprocess.run(
            ["bash", "-e", "-c", command],
            capture_output=True,
            text=True,
            env={**os.environ, **ENVIRONMENT},
            timeout=30,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertRegex(result.stdout, r"Scorecard exit status: [1-9][0-9]*")
        output = Path(result.stdout.split("Report path: ", 1)[1].strip())
        self.assertTrue(output.is_relative_to(self.root))
        scores = {
            check["name"]: check["score"]
            for check in json.loads(output.read_text())["checks"]
        }
        self.assertGreaterEqual(scores["License"], 0)
        self.assertEqual(-1, scores["Token-Permissions"])

    def test_explicit_non_file_check_is_rejected_in_local_mode(self):
        output = self.root / "unsupported.json"
        scan = self.scan("Branch-Protection", output)
        self.assertNotEqual(0, scan.returncode)
        self.assertIn("Unsupported RequestType", scan.stderr)
        self.assertFalse(output.exists())

    def test_failed_scan_has_no_fresh_report_and_cannot_reuse_baseline(self):
        baseline = self.root / "baseline.json"
        scan = self.scan("License", baseline)
        self.assertEqual(0, scan.returncode, scan.stderr)
        original = baseline.read_bytes()
        output = self.root / "failed.json"
        failed = self.scan("Not-A-Real-Check", output)
        self.assertNotEqual(0, failed.returncode)
        self.assertFalse(output.exists())
        self.assertEqual(original, baseline.read_bytes())
        with self.assertRaises(FileNotFoundError):
            output.read_text()
        with self.assertRaisesRegex(AssertionError, "fresh destination"):
            self.scan("License", baseline)

    def test_truncated_cli_output_is_not_a_usable_measurement(self):
        output = self.root / "local.json"
        scan = self.scan("License", output)
        self.assertEqual(0, scan.returncode, scan.stderr)
        original = output.read_bytes()
        self.assertEqual("License", json.loads(original)["checks"][0]["name"])
        # Model an interrupted copy of actual upstream JSON, not a scanner defect.
        damaged = self.root / "truncated.json"
        damaged.write_bytes(original[: len(original) // 2])
        with self.assertRaises(json.JSONDecodeError):
            json.loads(damaged.read_text())
        self.assertEqual(original, output.read_bytes())


if __name__ == "__main__":
    unittest.main()

"""The pull-request and release-tag checks, against throwaway git repositories."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_check  # noqa: E402

# Keep the maintainer's own git and GnuPG settings, such as automatic signing, out of the tests.
ISOLATED = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Tester",
    "GIT_AUTHOR_EMAIL": "tester@example.test",
    "GIT_COMMITTER_NAME": "Tester",
    "GIT_COMMITTER_EMAIL": "tester@example.test",
}


class Repository:
    """A scratch repository whose main branch stands in for origin/main."""

    def __init__(self, directory: Path) -> None:
        self.path = directory
        self.git("init", "--quiet", "--initial-branch=main")

    def git(self, *arguments: str, env: dict | None = None) -> str:
        return release_check.git(*arguments, cwd=self.path, env=env or ISOLATED)

    def commit(
        self, *, version: str, pin: str = "server==1.0.0", changelog: str = ""
    ) -> None:
        manifest = self.path / release_check.MANIFEST
        manifest.parent.mkdir(exist_ok=True)
        manifest.write_text(json.dumps({"name": "plugin", "version": version}))
        (self.path / release_check.MCP_REQUIREMENTS).write_text(
            f"# The server.\n{pin}\n"
        )
        (self.path / release_check.CHANGELOG).write_text(changelog)
        self.git("add", "--all")
        self.git(
            "commit", "--quiet", "--allow-empty", "--message", f"version {version}"
        )

    def check(self, tag: str, **options):
        options.setdefault("require_signature", False)
        return release_check.check_tag(tag, cwd=self.path, main_ref="main", **options)


class ScratchRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repo = Repository(Path(directory.name))
        self.environment = unittest.mock.patch.dict(os.environ, ISOLATED)
        self.environment.start()
        self.addCleanup(self.environment.stop)


class PinBumpTest(ScratchRepositoryTest):
    def problems(self) -> list[str]:
        return release_check.check_pin_bump("HEAD~1", "HEAD", cwd=self.repo.path)

    def test_a_changed_pin_needs_a_changed_plugin_version(self) -> None:
        self.repo.commit(version="1.0.0", pin="server==1.0.0")
        self.repo.commit(version="1.0.0", pin="server==1.1.0")
        [problem] = self.problems()
        self.assertIn("server==1.1.0", problem)

    def test_a_changed_pin_with_a_changed_version_passes(self) -> None:
        self.repo.commit(version="1.0.0", pin="server==1.0.0")
        self.repo.commit(version="1.1.0", pin="server==1.1.0")
        self.assertEqual([], self.problems())

    def test_changes_that_leave_the_pin_alone_need_no_version_change(self) -> None:
        self.repo.commit(version="1.0.0", changelog="first")
        self.repo.commit(version="1.0.0", changelog="second")
        self.assertEqual([], self.problems())

    def test_a_base_without_a_pin_file_is_not_a_pin_change(self) -> None:
        self.repo.git("commit", "--quiet", "--allow-empty", "--message", "empty")
        self.repo.commit(version="1.0.0")
        self.assertEqual([], self.problems())


class TagTest(ScratchRepositoryTest):
    NOTES = "### Changed\n\n- An arbitrary line of release notes."

    def release_commit(self, version: str = "2.3.4") -> None:
        changelog = f"# Changelog\n\n## [{version}] - 2000-01-01\n\n{self.NOTES}\n\n## [0.0.1]\n\nOld.\n"
        self.repo.commit(version=version, changelog=changelog)

    def annotate(self, tag: str) -> None:
        self.repo.git("tag", "--annotate", "--message", tag, tag)

    def test_a_matching_annotated_tag_on_main_yields_its_changelog_entry(self) -> None:
        self.release_commit()
        self.annotate("v2.3.4")
        self.assertEqual(([], self.NOTES), self.repo.check("v2.3.4"))

    def test_problems_are_reported_for_tags_that_do_not_qualify(self) -> None:
        self.release_commit()
        self.repo.git("tag", "v2.3.4")  # lightweight
        self.annotate("v9.9.9")  # not the plugin's version
        self.repo.git("switch", "--quiet", "--create", "side")
        self.repo.commit(version="3.0.0", changelog="## 3.0.0\n\nNotes.\n")
        self.annotate("v3.0.0")  # not on main
        self.repo.git("switch", "--quiet", "main")
        self.repo.commit(version="4.0.0", changelog="## [3.9.9]\n\nAnother version.\n")
        self.annotate("v4.0.0")  # no changelog entry
        self.repo.commit(version="5.0", changelog="## 5.0\n\nNotes.\n")
        self.annotate("v5.0")  # not a semantic version

        for tag, expected in (
            ("v2.3.4", "lightweight"),
            ("v9.9.9", "expected the tag v2.3.4"),
            ("v3.0.0", "is not on main"),
            ("v4.0.0", "no entry for 4.0.0"),
            ("v5.0", "no semantic version"),
            ("v0.0.0", "no tag named"),
        ):
            with self.subTest(tag=tag):
                problems, _ = self.repo.check(tag)
                self.assertEqual(1, len(problems), problems)
                self.assertIn(expected, problems[0])

    def test_an_empty_changelog_section_is_not_an_entry(self) -> None:
        self.assertIsNone(
            release_check.changelog_entry("## [1.0.0]\n\n## [0.9.0]\n\nx\n", "1.0.0")
        )
        self.assertEqual(
            "x", release_check.changelog_entry("## 0.9.0 (old)\n\nx\n", "0.9.0")
        )

    def test_prerelease_versions_are_recognized(self) -> None:
        self.assertTrue(release_check.is_prerelease("v1.0.0-beta.1"))
        self.assertFalse(release_check.is_prerelease("v1.0.0"))


class SignatureTest(ScratchRepositoryTest):
    """Signed tags, checked against a directory holding only the release keys."""

    SIGNER = "release@example.test"

    def setUp(self) -> None:
        super().setUp()
        self.repo.commit(version="1.2.3", changelog="## [1.2.3]\n\nNotes.\n")
        self.keys = self.directory("keys-")

    def directory(self, prefix: str) -> Path:
        path = tempfile.mkdtemp(prefix=prefix, dir=release_check._short_temp())
        self.addCleanup(shutil.rmtree, path, ignore_errors=True)
        return Path(path)

    def problems(self, keys: Path | None = None) -> list[str]:
        found, _ = self.repo.check(
            "v1.2.3", require_signature=True, keys=keys or self.keys
        )
        return found

    def sign(self, *options: str, env: dict | None = None) -> None:
        self.repo.git(
            *options, "tag", "--sign", "--message", "v1.2.3", "v1.2.3", env=env
        )

    def openpgp_key(self, name: str) -> tuple[dict, bytes]:
        """Create an OpenPGP signing key; return its environment and public key."""

        env = {**ISOLATED, "GNUPGHOME": str(self.directory("k-"))}
        self.addCleanup(
            subprocess.run, ["gpgconf", "--kill", "all"], env=env, capture_output=True
        )
        generate = [
            "gpg",
            "--batch",
            "--quiet",
            "--passphrase",
            "",
            "--quick-generate-key",
        ]
        subprocess.run(
            [*generate, name, "ed25519", "sign", "never"], env=env, check=True
        )
        export = ["gpg", "--batch", "--armor", "--export"]
        return env, subprocess.run(
            export, env=env, check=True, capture_output=True
        ).stdout

    def ssh_key(self) -> tuple[Path, str]:
        """Create an SSH signing key; return its path and its allowed-signers line."""

        key = self.directory("s-") / "key"
        generate = ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", self.SIGNER]
        subprocess.run([*generate, "-f", str(key)], check=True)
        public = key.with_suffix(".pub").read_text().split()
        return key, f'{self.SIGNER} namespaces="git" {public[0]} {public[1]}\n'

    @unittest.skipUnless(shutil.which("gpg"), "GnuPG is needed to create this tag")
    def test_a_tag_signed_with_a_published_openpgp_key_is_accepted(self) -> None:
        signer, public = self.openpgp_key(f"Release Signer <{self.SIGNER}>")
        _, other = self.openpgp_key("Someone Else <else@example.test>")
        self.sign("-c", f"user.signingkey={self.SIGNER}", env=signer)
        (self.keys / release_check.OPENPGP_KEYS).write_bytes(public)
        self.assertEqual([], self.problems())
        (self.keys / release_check.OPENPGP_KEYS).write_bytes(other)
        self.assertEqual(1, len(self.problems()))

    @unittest.skipUnless(
        shutil.which("ssh-keygen"), "OpenSSH is needed to create this tag"
    )
    def test_a_tag_signed_with_a_published_ssh_key_is_accepted(self) -> None:
        key, signer = self.ssh_key()
        _, other = self.ssh_key()
        self.sign("-c", "gpg.format=ssh", "-c", f"user.signingkey={key}.pub")
        (self.keys / release_check.SSH_SIGNERS).write_text(signer)
        self.assertEqual([], self.problems())
        (self.keys / release_check.SSH_SIGNERS).write_text(other)
        self.assertEqual(1, len(self.problems()))

    def test_a_signature_is_required_and_needs_published_keys(self) -> None:
        self.repo.git("tag", "--annotate", "--message", "v1.2.3", "v1.2.3")
        [no_keys] = self.problems()
        self.assertIn("No release keys are published", no_keys)
        (self.keys / release_check.SSH_SIGNERS).write_text(self.ssh_key()[1])
        [unsigned] = self.problems()
        self.assertIn("valid signature", unsigned)


if __name__ == "__main__":
    unittest.main()

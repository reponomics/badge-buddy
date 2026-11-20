#!/usr/bin/env python3
"""Checks that gate a pull request and a release tag.

``pin-bump``: a change to the pinned MCP server version must come with a change to the
plugin version, because users receive a new copy of the plugin only when its version
changes.

``tag``: a release tag must be an annotated tag signed with a release key, be named for
the plugin version it points at, sit on the main branch, and have a changelog entry.
The entry is written out as the release notes.

Run both from a checkout of the main branch, so that the release keys and this script
are the reviewed ones and not those of the commit being checked.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ".claude-plugin/plugin.json"
MCP_REQUIREMENTS = "requirements-mcp.txt"
CHANGELOG = "CHANGELOG.md"
# Public keys that may sign a release tag, read from the checkout this script runs in.
RELEASE_KEYS = ROOT / "docs" / "release"
OPENPGP_KEYS = "signing-keys.asc"
SSH_SIGNERS = "allowed_signers"
# https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEMVER = re.compile(
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
)


def git(*arguments: str, cwd: Path, env: dict[str, str] | None = None) -> str:
    """Return a git command's output; raise if the command fails."""

    completed = subprocess.run(  # noqa: S603
        ["git", *arguments],  # noqa: S607
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout


def file_at(ref: str, path: str, *, cwd: Path) -> str | None:
    """Return a file's text as committed at ``ref``, or None when it is absent there."""

    try:
        return git("show", f"{ref}:{path}", cwd=cwd)
    except subprocess.CalledProcessError:
        return None


def plugin_version(ref: str, *, cwd: Path) -> str | None:
    manifest = file_at(ref, MANIFEST, cwd=cwd)
    if manifest is None:
        return None
    version = json.loads(manifest).get("version")
    return version if isinstance(version, str) else None


def mcp_pin(ref: str, *, cwd: Path) -> str | None:
    """Return the requirement line that pins the MCP server at ``ref``."""

    requirements = file_at(ref, MCP_REQUIREMENTS, cwd=cwd)
    if requirements is None:
        return None
    lines = [line.strip() for line in requirements.splitlines()]
    pins = [line for line in lines if line and not line.startswith("#")]
    return pins[0] if len(pins) == 1 else None


def check_pin_bump(base: str, head: str, *, cwd: Path) -> list[str]:
    """Report a changed MCP pin that is not accompanied by a changed plugin version."""

    before, after = mcp_pin(base, cwd=cwd), mcp_pin(head, cwd=cwd)
    if before is None or before == after:
        return []
    if plugin_version(base, cwd=cwd) != plugin_version(head, cwd=cwd):
        return []
    return [
        f"The MCP pin changed from {before!r} to {after!r} but the version in {MANIFEST} "
        "did not. Users keep their installed copy until the plugin version changes, so "
        "raise the version and add a changelog entry in the same pull request."
    ]


def changelog_entry(changelog: str, version: str) -> str | None:
    """Return the body of the changelog section for ``version``, or None if there is none.

    A section starts at a second-level heading whose first word is the version, with or
    without brackets, and runs to the next second-level heading.
    """

    body: list[str] | None = None
    for line in changelog.splitlines():
        if line.startswith("## "):
            if body is not None:
                break
            title = line[3:].strip().split()[0] if line[3:].strip() else ""
            if title.strip("[]") == version:
                body = []
        elif body is not None:
            body.append(line)
    if body is None:
        return None
    text = "\n".join(body).strip()
    return text or None


def signature_problem(tag: str, keys: Path, *, cwd: Path) -> str | None:
    """Verify the tag's signature against only the release keys published in ``keys``.

    Either kind of key git can sign with is accepted: OpenPGP public keys in
    ``signing-keys.asc``, SSH keys in ``allowed_signers``, or both.
    """

    openpgp, ssh = keys / OPENPGP_KEYS, keys / SSH_SIGNERS
    if not openpgp.is_file() and not ssh.is_file():
        return f"No release keys are published: add {OPENPGP_KEYS} or {SSH_SIGNERS} to {keys}."
    # An empty keyring, so that only the published keys can vouch for the tag. The path is
    # short because GnuPG refuses socket paths longer than the platform's limit.
    with tempfile.TemporaryDirectory(prefix="rk-", dir=_short_temp()) as home:
        env = {**os.environ, "GNUPGHOME": home}
        if openpgp.is_file():
            imported = subprocess.run(  # noqa: S603
                ["gpg", "--batch", "--quiet", "--import", str(openpgp)],  # noqa: S607
                env=env,
                text=True,
                capture_output=True,
            )
            if imported.returncode != 0:
                return f"Could not read {openpgp.name}: {imported.stderr.strip()}"
        signers = ["-c", f"gpg.ssh.allowedSignersFile={ssh}"] if ssh.is_file() else []
        verified = subprocess.run(  # noqa: S603
            ["git", *signers, "verify-tag", tag],  # noqa: S607
            cwd=cwd,
            env=env,
            capture_output=True,
        )
    if verified.returncode != 0:
        return (
            f"Tag {tag} does not carry a valid signature from a published release key. "
            f'Create it with: git tag -s {tag} -m "{tag}"'
        )
    return None


def _short_temp() -> str | None:
    return "/tmp" if Path("/tmp").is_dir() else None  # noqa: S108


def check_tag(
    tag: str,
    *,
    cwd: Path,
    main_ref: str = "origin/main",
    keys: Path = RELEASE_KEYS,
    require_signature: bool = True,
) -> tuple[list[str], str | None]:
    """Return the problems with a release tag, and its release notes when it has them."""

    ref = f"refs/tags/{tag}"
    try:
        kind = git("cat-file", "-t", ref, cwd=cwd).strip()
    except subprocess.CalledProcessError:
        return [f"There is no tag named {tag}."], None

    problems: list[str] = []
    if kind != "tag":
        problems.append(
            f"Tag {tag} is a lightweight tag. A release tag must be an annotated, signed tag."
        )
    elif require_signature:
        problem = signature_problem(tag, keys, cwd=cwd)
        if problem:
            problems.append(problem)

    commit = f"{ref}^{{commit}}"
    version = plugin_version(commit, cwd=cwd)
    if version is None or not SEMVER.fullmatch(version):
        problems.append(f"{MANIFEST} at {tag} has no semantic version: {version!r}.")
    elif tag != f"v{version}":
        problems.append(
            f"Tag {tag} points at plugin version {version}; expected the tag v{version}."
        )

    on_main = subprocess.run(  # noqa: S603
        ["git", "merge-base", "--is-ancestor", commit, main_ref],  # noqa: S607
        cwd=cwd,
        capture_output=True,
    )
    if on_main.returncode != 0:
        problems.append(f"The commit that {tag} points at is not on {main_ref}.")

    notes = None
    if version is not None:
        notes = changelog_entry(file_at(commit, CHANGELOG, cwd=cwd) or "", version)
        if notes is None:
            problems.append(f"{CHANGELOG} at {tag} has no entry for {version}.")
    return problems, notes


def is_prerelease(tag: str) -> bool:
    match = SEMVER.fullmatch(tag.removeprefix("v"))
    return bool(match and match.group(4))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    pin = commands.add_parser(
        "pin-bump", help="check a pull request's MCP pin and version"
    )
    pin.add_argument(
        "--base", required=True, help="commit the change is compared against"
    )
    pin.add_argument("--head", default="HEAD")
    release = commands.add_parser("tag", help="check a release tag and write its notes")
    release.add_argument("--tag", required=True)
    release.add_argument("--main-ref", default="origin/main")
    release.add_argument(
        "--notes-out", type=Path, help="file to write the release notes to"
    )
    args = parser.parse_args(argv)

    if args.command == "pin-bump":
        problems = check_pin_bump(args.base, args.head, cwd=ROOT)
    else:
        problems, notes = check_tag(args.tag, cwd=ROOT, main_ref=args.main_ref)
        if not problems and args.notes_out is not None:
            args.notes_out.write_text(f"{notes}\n", encoding="utf-8")
    for problem in problems:
        print(f"error: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())

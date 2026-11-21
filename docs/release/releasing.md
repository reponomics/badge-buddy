# Releasing

This page is for maintainers. A release is a version change merged to `main`, a tag that a maintainer signs on their own machine, and a GitHub release that a workflow publishes after checking the tag.

For an agent-guided or explicitly authorized autonomous release, use the [release assistant routine](assistant.md). It explains how to discover current state, respect the requested stopping point, resume safely, and verify completion using this procedure.

The proposed separation of development from marketplace distribution, the old marketplace transition, and verification limits are recorded in [Marketplace distribution and verification research](marketplace-distribution.md). That design and its disposable rehearsal are pending; they are not implemented by the procedure below.

## Cut a release

For the current maintainer's checkout, select OpenPGP signing and the published `git-dev` key explicitly. These settings apply only to this repository:

```bash
git config --local gpg.format openpgp
git config --local user.signingkey BA1F75AD253CF32E8C4DE9E98339CEC9D2C12CB2
```

The corresponding private key must be available through the maintainer's local GPG installation. Only its public key is committed to this repository. See [Release keys](verification.md#release-keys) for the signing identity and full fingerprint.

1. Open a pull request that sets the new version in [.claude-plugin/plugin.json](../../.claude-plugin/plugin.json) and, in [CHANGELOG.md](../../CHANGELOG.md), moves the entries under `Unreleased` to a heading for the version, such as `## [1.2.3] - 2027-01-15`. Read the entry as release notes: it is published as written. Merge the pull request.
2. After the merged release commit passes CI, update your checkout and identify that commit's full SHA. The tag name is `badge-buddy--v` followed by the manifest version. Replace `<release-commit-sha>` below with that SHA; later commits may land on `main` without becoming part of this release:

   ```bash
   git switch main
   git pull --ff-only origin main
   ```

   ```bash
   git tag -s badge-buddy--v1.2.3 <release-commit-sha> -m "Badge Buddy 1.2.3"
   ```

   ```bash
   python3 tools/release_check.py tag --tag badge-buddy--v1.2.3
   git push origin refs/tags/badge-buddy--v1.2.3
   ```

3. The [release workflow](../../.github/workflows/release.yml) runs on the tag. It refuses the tag unless it is annotated, carries a valid signature from a published release key, matches the plugin version at that commit, points at a commit on `main`, and has a changelog entry. It then runs `make check` on the tagged commit.
4. Approve the `release` environment when asked. The workflow publishes the GitHub release with the changelog entry as its notes and confirms that the release is immutable.
5. Run the commands in [Verifying a release](verification.md) against the new tag.

A version with a prerelease suffix, such as `1.3.0-beta.1`, uses the tag `badge-buddy--v1.3.0-beta.1` and is published as a prerelease. The plugin-name hyphens and build metadata do not make a stable version a prerelease.

Merging the version PR does not publish a GitHub release; pushing the tag triggers publication. The marketplace currently follows `main`, so marketplace installation is not gated on that publication. No additional catalog promotion or legacy-user migration is required for `0.4.0-beta.1`.

## Scorecard integration acceptance

Before releasing the CLI/MCP integration or changing its compatibility baseline:

- Verify that the plugin version advances and the changelog describes the required executable, any command changes, and compatibility policy. `tools/release_check.py pin-bump` watches the Best Practices package only; it does not enforce these Scorecard changes.
- Run `make check`, `make test-live`, `make test-scorecard`, and `make plugin-validate`. Confirm the separate Scorecard CI job passes with its checksum-verified release binary; a local macOS run does not establish the Linux CI result.
- Exercise the [Scorecard evaluation scenarios](../../tests/scorecard-skill-evals.md) for installation, executable identity, missing dependency, connection, and skill routing. Review local execution evidence with the maintainer. Treat unrun cases or failed measurements explicitly when deciding release readiness.
- Review integration coverage for the final candidate, including application/review, Scorecard diagnosis, recovery, and cross-skill behavior. Keep execution records private and identify any release-relevant gaps.
- Inspect the release commit's file inventory: `.mcp.json`, the skill and every linked reference, and `scripts/scorecard.py` must be included. The current release uses the repository snapshot; there is no separate generated plugin bundle. Never ship a developer's executable, credentials, or temporary evaluation state.

The manifest version can identify a pending release while its notes remain under `Unreleased`; move those notes to a dated version heading as part of the release pull request before tagging.

## If something goes wrong

Never move or reuse a tag that has been pushed: consumers can fetch it even before a GitHub release exists. If the tagged content is wrong, fix it in a new version. If publication failed because of a repository setting or a transient service failure, correct the cause and rerun the workflow for the unchanged tag. A tag that has never left the local checkout can be corrected before pushing.

To check a tag before pushing it, run the same check locally from a checkout of `main`:

```bash
python3 tools/release_check.py tag --tag badge-buddy--v1.2.3
```

## Release keys

`docs/release/signing-keys.asc` holds the OpenPGP public keys that may sign a release, and `docs/release/allowed_signers` holds SSH public keys in git's allowed-signers format. The workflow reads them from `main`, so a key takes effect only after the pull request that adds it is merged. Keep private keys off GitHub: do not store one as a repository or environment secret, and do not sign tags in a workflow.

To add an OpenPGP key, append its public key to the file:

```bash
gpg --armor --export <key-id> >> docs/release/signing-keys.asc
```

The files above authorize keys for new releases. When a key is retired, remove it from these authorization files and preserve its public key separately for historical verification, with its fingerprint and the releases it signed documented. Announce any replacement key and its effective release in the changelog. Do not leave a retired key authorized merely to preserve historical verification.

## Repository settings the process relies on

| Setting | Why |
| --- | --- |
| Immutable releases enabled | A published tag and its release cannot be changed; the workflow fails if this is off |
| A `release` environment with required reviewers | Publishing waits for a maintainer's approval |
| A ruleset on `main` requiring pull requests and the CI, CodeQL, and dependency scan checks | Everything a tag can point at has passed review and checks |
| Secret scanning with push protection | Credentials do not reach the repository |
| Dependabot alerts | Known vulnerabilities in the pinned MCP server and the development tools are reported |

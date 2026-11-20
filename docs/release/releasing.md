# Releasing

This page is for maintainers. A release is a version change merged to `main`, a tag that a maintainer signs on their own machine, and a GitHub release that a workflow publishes after checking the tag.

## Cut a release

1. Open a pull request that sets the new version in [.claude-plugin/plugin.json](../../.claude-plugin/plugin.json) and, in [CHANGELOG.md](../../CHANGELOG.md), moves the entries under `Unreleased` to a heading for the version, such as `## [1.2.3] - 2027-01-15`. Read the entry as release notes: it is published as written. Merge the pull request.
2. Update your checkout of `main`, then sign and push the tag. The tag name is `v` followed by the version:

   ```bash
   git switch main && git pull --ff-only
   ```

   ```bash
   git tag -s v1.2.3 -m "Badge Buddy 1.2.3"
   ```

   ```bash
   git push origin v1.2.3
   ```

3. The [release workflow](../../.github/workflows/release.yml) runs on the tag. It refuses the tag unless it is annotated, carries a valid signature from a published release key, matches the plugin version at that commit, points at a commit on `main`, and has a changelog entry. It then runs `make check` on the tagged commit.
4. Approve the `release` environment when asked. The workflow publishes the GitHub release with the changelog entry as its notes and confirms that the release is immutable.
5. Run the commands in [Verifying a release](verification.md) against the new tag.

A version with a prerelease suffix, such as `1.3.0-beta.1`, is published as a prerelease.

## If something goes wrong

Never move or delete a published tag. If a release is wrong, fix it in a new version.

If the workflow refuses a tag that has no GitHub release yet, the tag has not been published as a release. Delete it, correct the problem, and tag again:

```bash
git push origin :refs/tags/v1.2.3
```

To check a tag before pushing it, run the same check locally from a checkout of `main`:

```bash
python3 tools/release_check.py tag --tag v1.2.3
```

## Release keys

`docs/release/signing-keys.asc` holds the OpenPGP public keys that may sign a release, and `docs/release/allowed_signers` holds SSH public keys in git's allowed-signers format. The workflow reads them from `main`, so a key takes effect only after the pull request that adds it is merged. Keep private keys off GitHub: do not store one as a repository or environment secret, and do not sign tags in a workflow.

To add an OpenPGP key, append its public key to the file:

```bash
gpg --armor --export <key-id> >> docs/release/signing-keys.asc
```

When a key is replaced, keep the old public key in the file so that earlier releases still verify, and note the change in the changelog.

## Repository settings the process relies on

| Setting | Why |
| --- | --- |
| Immutable releases enabled | A published tag and its release cannot be changed; the workflow fails if this is off |
| A `release` environment with required reviewers | Publishing waits for a maintainer's approval |
| A ruleset on `main` requiring pull requests and the CI, CodeQL, and dependency scan checks | Everything a tag can point at has passed review and checks |
| Secret scanning with push protection | Credentials do not reach the repository |
| Dependabot alerts | Known vulnerabilities in the pinned MCP server and the development tools are reported |

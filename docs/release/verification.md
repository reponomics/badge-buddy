# Verifying a release

A Badge Buddy release is a git tag named `v<version>` on the `main` branch. The tag is annotated and cryptographically signed by a maintainer, and it has a GitHub release that carries the release notes. Maintainers must enable GitHub release immutability before publishing; the verification steps below check that the published release is immutable.

Claude Code installs a plugin by cloning its repository and does not check signatures. The checks on this page use git with GnuPG or OpenSSH, and none of them depends on Claude Code.

An install that follows `main` gets reviewed code but is not tied to a release. To install one specific release and verify it, pin the marketplace to its tag, check the tag's signature, and compare the installed files with the signed commit, as described here.

## Install a specific release

Replace `v1.2.3` with the release you want:

```bash
claude plugin marketplace add 'reponomics/badge-buddy#v1.2.3'
```

```bash
claude plugin install badge-buddy@badge-buddy
```

A pinned install stays on that release; updating the plugin does not move it. To move to a newer release, register the marketplace at the newer tag. If your version of Claude Code needs the old registration removed first, be aware that removing a marketplace also uninstalls its plugins.

## Release keys

The current release signer is **Really Him ([hesreallyhim](https://github.com/hesreallyhim)), `git-dev@hesreallyhim.com`**, using this OpenPGP primary-key fingerprint:

```text
BA1F 75AD 253C F32E 8C4D E9E9 8339 CEC9 D2C1 2CB2
```

Download the public key from [signing-keys.asc](signing-keys.asc). The same key is published in the maintainer's [GitHub public-key bundle](https://github.com/hesreallyhim.gpg), which may contain other keys that are not authorized to sign Badge Buddy releases. Compare the full fingerprint above, not just the name or email address.

The public keys that may sign a release are published in this repository's `main` branch, in `docs/release/`:

| File | Key type | Used by |
| --- | --- | --- |
| `signing-keys.asc` | OpenPGP public keys | `gpg` and `git verify-tag` |
| `allowed_signers` | SSH public keys, in git's allowed-signers format | `git verify-tag` |

Either file, or both, may be present. The private keys are held by the maintainers who sign and are never stored on GitHub or used by a workflow.

These files are the project's statement of who may sign. So that you do not rely on one copy alone, compare a key's fingerprint with the one shown on earlier releases or on the signer's own GitHub profile. This prints the fingerprints of the OpenPGP keys:

```bash
gpg --show-keys --with-fingerprint docs/release/signing-keys.asc
```

## Check a tag's signature

Clone the repository and fetch the tag:

```bash
git clone https://github.com/reponomics/badge-buddy.git
```

```bash
cd badge-buddy && git fetch origin 'refs/tags/v1.2.3:refs/tags/v1.2.3'
```

For a tag signed with an OpenPGP key, import the release keys and verify:

```bash
gpg --import docs/release/signing-keys.asc
```

```bash
git verify-tag v1.2.3
```

For a tag signed with an SSH key:

```bash
git -c gpg.ssh.allowedSignersFile=docs/release/allowed_signers verify-tag v1.2.3
```

A good result names the signer and reports a good signature. Take the keys from `main`, as above, and not from the tag you are checking.

## Check the release on GitHub

With the [GitHub CLI](https://cli.github.com/), confirm that the release is immutable and which commit it names:

```bash
gh release verify v1.2.3 --repo reponomics/badge-buddy
```

```bash
git rev-parse 'v1.2.3^{commit}'
```

The commit that `git rev-parse` prints is the one the signed tag points at.

## Compare the installed copy with the signed commit

Claude Code loads the plugin from a copy it keeps in its plugin cache. To see that this copy is the release you verified, check out the tag in your clone and compare the two directories yourself.

Find the directory Claude Code loads the plugin from; it is the `installPath` of `badge-buddy@badge-buddy`:

```bash
claude plugin list --json
```

Then, from your clone:

```bash
git switch --detach v1.2.3
```

```bash
diff -r --exclude=.git . "<installPath>"
```

The installed copy has no `.git` directory, and Claude Code may add bookkeeping files of its own to it, such as `.in_use`. Any other difference means the installed copy is not that release.

## What this does and does not establish

A verified tag shows that a holder of a release key signed that exact commit under that version name, and that the tag has not been changed since. It does not show that the code is free of defects, and it says nothing about the MCP server, which is a separate project with its own [release verification](https://github.com/reponomics/best-practices-mcp/blob/main/docs/release/verification.md).

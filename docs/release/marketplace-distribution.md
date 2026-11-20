# Marketplace distribution and verification research

Reviewed on 2026-11-19. This note records a proposed distribution change, its trust assumptions, and a rehearsal plan. It is not an implemented release procedure. Neither marketplace has been redirected, and the rehearsal has not been run.

Release scope decision: `0.4.0-beta.1` keeps the standalone marketplace following `main` and assumes no existing consumers of the previous implementation. Migration, catalog promotion, archive distribution, and reusable verification tooling are deferred. The old marketplace can distribute the standalone plugin later without making migration support a release requirement.

## What is currently deployed

The standalone catalog in [marketplace.json](../../.claude-plugin/marketplace.json) lists Badge Buddy with `"source": "./"`. The live [`reponomics/plugins` catalog](https://github.com/reponomics/plugins/blob/main/.claude-plugin/marketplace.json), checked during this review, still lists the old implementation at `./plugins/badge-buddy`. Both manifests declared `0.3.0-beta.1` when this research began; standalone release preparation now sets its manifest to `0.4.0-beta.1`.

The standalone repository's release workflow checks signed Git tags and publishes a GitHub release. It does not produce a plugin ZIP or advance a marketplace pointer. Release preparation aligns the trigger, checker, tests, and examples with `badge-buddy--v<version>` and makes prerelease detection examine the version suffix rather than the plugin-name hyphens.

## Catalog authority and source changes

A marketplace identifies an installed plugin by its entry name and marketplace name. The entry separately declares where to fetch the plugin. The documented schema permits a relative path or an external Git repository, including a tag or commit pin. Thus keeping `badge-buddy@reponomics` while replacing its source with the new repository is representable in the catalog. See the [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference#plugin-sources).

That establishes schema support, not a tested migration guarantee. The reviewed documentation does not establish whether an ordinary Git source change receives a fresh consent prompt. Test the actual update behavior before describing it as seamless or silent. A command-source consent mechanism is documented separately and should not be assumed to apply to Git sources.

The security consequence is that catalog control includes authority to select plugin code and its upstream publisher. A compromised catalog can substitute a source; it can also replace code already stored in the marketplace repository. Changing repositories is therefore an important change to review, even though catalog write access already carries substantial authority. A source pin limits what is downloaded from an unchanged entry; it does not stop someone authorized to edit the catalog from replacing the pin.

Anthropic documents that plugins can execute code with the user's privileges, and that plugin hooks and server processes run outside the tool-call sandbox. Its marketplace allowlist controls marketplace sources, not every plugin repository an allowed catalog references. See [plugin security](https://code.claude.com/docs/en/plugins/security) and [limits of managed plugin settings](https://code.claude.com/docs/en/plugins/org#plan-for-what-managed-settings-cant-enforce).

## Three different kinds of checks

| Check | What it establishes | What it does not establish |
| --- | --- | --- |
| `claude plugin validate --strict` | The distributed Claude CLI accepts the manifest and the content checks it performs | Publisher authorization, absence of malicious code, or correctness of Claude Code's implementation |
| An archive source's `sha256` | According to the documented installer behavior, the downloaded ZIP must match the digest in the catalog | An independently trusted publisher identity; a catalog editor can change both the URL and digest |
| Git tag or artifact signature verification against an independently selected identity | The signed object or artifact matches what that signing identity authorized | Safety of its contents, or that Claude Code performed the same check and loaded those exact files |

The archive integrity check is real documented functionality, distinct from manifest validation: `source: "archive"` takes an HTTPS ZIP URL and an optional `sha256`; a mismatched digest is refused. Its root may be at the ZIP's top level or one directory down. See [archive sources](https://code.claude.com/docs/en/plugins/marketplace-reference#archive-plugin-source).

Using that built-in check relies on the distributed Claude Code implementation. Closed-source implementation does not make a hash check meaningless, but it limits independent inspection and reproducibility of the verifier. We can check the archive's SHA-256 and its publisher signature with independent tools before installation. The expected digest or signing identity must itself come from a trusted source. We have not found a documented plugin-install policy that requires our OpenPGP signature; publishing one must not be described as automatic enforcement by Claude Code.

## Proposed release distribution

Keep the catalog on `main` and point the plugin entry at an already published release. Normal development can continue on `main`. Prepare the version and changelog in a PR, tag the exact merged release commit locally, verify and publish the release, then advance the catalog in a second PR. Do not merge a catalog pointer to a nonexistent tag or artifact.

Two source forms are worth rehearsing:

- A `github` source with the release tag and optionally the full commit SHA. When both `ref` and `sha` are supplied, Claude Code checks out the SHA; it is not a cryptographic proof that the named tag authorizes it.
- An `archive` source with a versioned, uploaded release ZIP and its SHA-256. This gives an artifact digest that can also be checked independently. Packaging, signing the artifact or its digest manifest, and checking the ZIP contents add work beyond the current signed-tag process.

Keep the plugin version in `plugin.json` rather than duplicating it in the catalog. The manifest version normally controls cache replacement, so changing a source while reusing a version is an explicit rehearsal case. Background updates for third-party marketplaces are off by default. See [version resolution](https://code.claude.com/docs/en/plugins/loading#versions-and-updates) and [marketplace updates](https://code.claude.com/docs/en/plugins/host-marketplace#keep-users-up-to-date).

Post-release promotion creates a documentation trap: the marketplace file inside a release tag may still point at the previous release. Adding `repo#release-tag` would pin that old catalog, not override its plugin source. Revise [exact-release installation](verification.md#install-a-specific-release) before adopting this design; a separately pinned catalog entry or loading a verified checkout avoids that ambiguity.

A pushed tag can be discovered by consumers before a GitHub release exists. Do not describe deleting and recreating an exposed tag as harmless recovery. Prefer a corrected version and preserve the failed release's history.

## Historical transition considerations (deferred)

The proposed compatibility option is to retain the `badge-buddy` entry in `reponomics`, point it at the maintained release, and stop developing the bundled implementation. The new repository and target release must be accessible to existing users first. This would preserve the install identity `badge-buddy@reponomics`; it also means advancing two catalog entries when a release is promoted. Rehearse this before changing the old catalog.

The [breaking-change notice](../../CHANGELOG.md#breaking-changes) still applies: old local drafts are not imported into MCP storage; answers saved to BadgeApp can be retrieved again. An update preserving the old install identity should retain its plugin data directory, but the new MCP deliberately does not read that directory. The new `uv` prerequisite also needs to be stated in the old marketplace's upgrade notice. Keep migration instructions out of the durable skill.

An explicit switch to `badge-buddy@badge-buddy` is a different installation. Disable the old plugin when switching. Do not tell users to remove the entire `reponomics` marketplace: that also uninstalls its other plugins. If uninstalling only the old plugin, consider `--keep-data` to retain unsynced drafts for manual recovery. The documented `renames` map resolves names within one marketplace; it does not transfer an installation between marketplaces. See [rename and removal behavior](https://code.claude.com/docs/en/plugins/host-marketplace#rename-or-remove-a-plugin) and [marketplace removal](https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-remove).

## Disposable rehearsal plan

Use two disposable repositories: one catalog initially containing a bundled dummy plugin, and one replacement plugin repository. Use a unique marketplace and plugin name, inert text-only skills, and marker files that identify each release. No hook, MCP server, real project draft, or production signing key is needed to test installation. Use a disposable signing identity only for the independent signing tests.

Run with an isolated `CLAUDE_CONFIG_DIR` and an empty working directory, preferably inside a disposable VM or container. A separate config directory isolates plugin settings and caches; it is not a security sandbox. Record the exact CLI version and platform. During this review the local CLI reported `2.1.327`, while the repository's CI dependency pins `2.1.328`; test the selected supported versions explicitly.

Archive sources require HTTPS and reject loopback hosts, so a localhost HTTP ZIP server is not a faithful supported fixture. Use disposable hosted release assets for that leg. GitHub-backed tests should use the intended `github` source type rather than claim a local path test proves identical behavior.

| Case | Evidence to collect |
| --- | --- |
| Fresh install from the original catalog | Installed identity, manifest version, marker contents, and any consent shown |
| Same identity, changed repository, same version | Whether files change, whether the old cache is reused, and any warning or consent |
| Same identity, changed repository, higher version | Whether the intended release loads; whether data and settings persist |
| Manual update versus background update | Catalog refresh, prompts, timing, and reload requirements tested separately |
| Missing or inaccessible target ref | Failure message and whether the previously installed plugin stays usable |
| Tag plus matching or different commit pin | Actual checked-out contents, independently compared with the selected commit |
| Archive with correct digest | Successful install and byte-for-byte comparison with expected plugin files |
| Archive with a deliberately wrong digest | Refusal, exit status, and absence of replacement files |
| Catalog changes archive URL and digest together | Whether the change is accepted and whether fresh consent is requested |
| Invalid signature but correct archive digest | Separate results for independent signature verification and Claude's digest check; do not conflate them |
| Catalog pinned to a release tag | Which plugin ref that historical catalog actually selects |
| Old and new marketplace identities | Confirm an intentional switch without affecting other marketplace plugins |

Retain redacted command output, catalog revisions, release and artifact hashes, and installed-file comparisons. Do not rely solely on `installed_plugins.json` as evidence of what code was installed. A successful run establishes observed behavior for those versions and environments, not a source audit or a permanent guarantee.

## Possible reusable automation

Rehearse the process before extracting a reusable workflow. The current personal signing key should remain local. A useful first component would verify a maintainer-signed tag against an explicitly configured public key, check version/changelog consistency, and publish only after those checks pass. If archives are adopted, add deterministic packaging, independent artifact verification, and a catalog promotion PR carrying the exact source and digest.

Keep repository policy explicit: accepted source repositories, signing identities, release commit requirements, destination catalog entries, and prerelease rules. Pin a reusable workflow to a reviewed commit and give write permissions only to the job that needs them. A workflow that proposes a catalog PR fits required-PR branch rules better than one that pushes directly to `main`.

A workflow can enforce publisher-side policy and supply independently verifiable evidence. It cannot make an unmodified Claude Code client enforce a publisher signature. Attestations, archive checksums, and personal OpenPGP signatures should remain separately named outputs with documented verification procedures. Reusability by itself does not establish a SLSA level.

## Existing public implementations

These examples were inspected in source during this review. Their workflows were not executed and their published signatures were not independently verified. Links to `main` describe the inspected implementation and may change.

| Project | Implemented behavior | Limit relevant to this proposal |
| --- | --- | --- |
| [Netresearch skill release workflow](https://github.com/netresearch/skill-repo-skill/blob/main/.github/workflows/release.yml), called by [markdown-to-pdf-skill](https://github.com/netresearch/markdown-to-pdf-skill/blob/main/.github/workflows/release.yml) | A reusable workflow checks an annotated tag's GitHub verification status and manifest version, builds plugin and skill ZIP/tar archives, generates checksums, signs the checksum file with keyless Cosign, verifies it, and creates attestations before uploading release assets | Closest archive/signing example found. The caller uses a mutable `@main` reference; GitHub's verified-tag result is not a project-specific signing-key allowlist. The archive commands do not establish reproducibility. Its [catalog](https://github.com/netresearch/claude-code-marketplace/blob/main/.claude-plugin/marketplace.json) uses Git sources, so it does not demonstrate Claude's archive digest check |
| [Microsoft apm-action](https://github.com/microsoft/apm-action/blob/main/action.yml), used by [zava-agent-config](https://github.com/DevExpGbb/zava-agent-config/blob/main/.github/workflows/release.yml) | `mode: release` packages bundles, generates SHA-256 sidecars, stages marketplace metadata, and publishes a release | Packaging and publishing automation, not evidence of publisher signature verification. It introduces the broader APM toolchain |
| [Gwenneg togi release caller](https://github.com/gwenneg/togi/blob/main/.github/workflows/release.yml) and [claude-ichiba catalog updater](https://github.com/gwenneg/claude-ichiba/blob/main/.github/workflows/update-marketplace.yml) | The [reusable workflow pinned by the inspected caller](https://github.com/gwenneg/claude-ichiba/blob/2cd3f7fbe4fe0a80ff28215c513042cc83f08b1f/.github/workflows/plugin-release.yml) checks tag annotation, publishes a release, and dispatches its URL to the marketplace. The updater resolves the commit and proposes a PR changing `source.ref` and `source.sha` | A concrete release-then-promotion design. Annotation is not signature verification. The current reusable workflow on `main` differs from the pinned version the caller executes |

These examples establish that reusable archive signing and reviewed catalog promotion exist. This bounded search did not verify a single implementation combining signed ZIP releases, an archive URL/digest promotion PR, and an end-to-end Claude archive installation test. Do not turn that result into a claim that no such implementation exists.

To find further examples, search GitHub code for distinctive combinations such as `"marketplace.json" "cosign"`, `"marketplace.json" "sha256"`, `"workflow_call" "plugin"`, and `"marketplace.json" "repository_dispatch"`. Follow each result to a real caller and inspect the exact reusable-workflow revision it pins. Distinguish a proposed design document from executable automation and a signature being published from a signature being verified.

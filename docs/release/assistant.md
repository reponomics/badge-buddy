# Release assistant routine

Use this routine when asked to guide, prepare, resume, or carry out a Badge Buddy version update or release. It is repository-local and usable by a fresh agent session. It coordinates existing checks and the release workflow; it does not replace them or introduce a second publishing implementation.

## Establish scope once

Read the user's current request and any explicit boundaries retained from the session. Briefly state the intended work before acting. Ask only for missing decisions that materially affect the result, such as an ambiguous target version or whether publication is intended. Existing authorization persists; do not ask again before every already-authorized step.

| Request | Working scope |
| --- | --- |
| “Guide me through a release” or “review release readiness” | Inspect state, explain decisions and blockers, and prepare requested local changes. Guide the user through external actions; do not assume publication permission. |
| “Update the version” or “prepare the release” | Prepare version/changelog changes and appropriate local checks. Stop before external publication unless the request also authorizes it. |
| “Open a release PR” | Prepare and validate changes, push the release branch, and open the requested PR. Do not infer permission to merge, tag, or publish. |
| “Release version X autonomously” | Carry authorized preparation, PR, checks, permitted merge, publication of the maintainer-supplied signed tag, workflow completion, and verification forward. Honor explicit stopping points; the signed tag must be supplied before publication can proceed. |

An autonomous request does not authorize bypassing repository rules, fabricating review or contributor acknowledgments, changing billing/visibility/protection settings, exposing private keys, or weakening verification. It can still encounter a missing maintainer-supplied signed tag or a required independent reviewer/environment approval. Complete all independent preparation, then report the exact remaining action and its source. Do not pretend these external requirements can always be automated. Signing arrangements are outside this public routine; use the project's maintainer signing procedure as the separate boundary.

Creating or editing this routine is not itself authorization to release anything.

## Read the current sources of truth

Read these from the actual repository; do not rely on a remembered version, branch, successful run, signer, or previous conversation:

- [Releasing](releasing.md) and [verification](verification.md): project procedure and trust model.
- [Plugin manifest](../../.claude-plugin/plugin.json), [marketplace manifest](../../.claude-plugin/marketplace.json), and [changelog](../../CHANGELOG.md): version, distribution, and notes.
- [Release checker](../../tools/release_check.py), [release workflow](../../.github/workflows/release.yml), and [CI workflow](../../.github/workflows/ci.yml): executable checks and publication behavior.
- [Contributing](../../CONTRIBUTING.md), [Makefile](../../Makefile), and applicable integration/evaluation records: validation expectations.

Treat `docs/plans/` and research documents as context, not evidence that a proposed feature or distribution change was implemented. Compare instructions with code and current remote settings. Resolve material contradictions before publishing; do not silently skip a gate because prose or a historical run says it once worked.

## 1. Inventory and choose the candidate

Inspect working-tree status, current branch and worktrees, remotes, local/remote tags, existing release PRs, releases, and relevant workflow runs. Verify the intended repository before making remote changes, especially when operating in a fork. Use available authenticated tooling without printing credentials. Fetch the needed remote refs when connectivity permits; do not force-update conflicting local tags.

Preserve unrelated edits. Prefer a clean dedicated worktree and a `codex/` branch when preparing a release would disturb ongoing work. Do not reset, clean, stash, or switch another task's working tree merely for convenience. A divergent local `main` is a reason to inspect or create an isolated checkout from the remote, not to force it into alignment.

Establish the target version from the request and the actual change scope. A version already present in the manifest may be a pending release, not a published version; inspect tags and releases before incrementing it again. Validate semantic version syntax, prerelease intent, and whether the target tag/version already exists.

The current tag convention is `badge-buddy--v<version>`. Changes to this convention require coordinated checker/workflow/documentation changes, not a release-time workaround.

Inspect how the intended marketplace installation resolves its source. When it follows `main`, merging can distribute changed plugin content before a GitHub release exists. Make that consequence explicit before the merge; respect the user's already-selected distribution policy. Do not invent a staging branch, update a different marketplace repository, or change distribution sources without the task covering that work.

## 2. Prepare the version and notes

Update `.claude-plugin/plugin.json` and finalize the appropriate `CHANGELOG.md` section as described in the release procedure. Use the actual release date, not a copied example date. Remove stale “planned version” text from finalized notes, preserve unrelated unreleased work when the selected scope excludes it, and keep one unambiguous entry for the release version.

Describe user-visible behavior and requirements accurately. For Scorecard, explicitly account for the required executable and tested compatibility baseline; the Best Practices pin-bump check does not enforce Scorecard integration/version changes. Do not claim that the hosted fork or its extra tools are included unless the plugin actually uses them.

Inspect the repository snapshot that users will receive, including referenced skills, scripts, manifests, and dependency pins. No generated bundle should be assumed. Exclude secrets, local test outputs, binaries, private planning, and machine-specific state from newly staged changes. Check the staged diff before committing.

Use conventional commits and the existing PR template. Describe the final behavior, actual validation, and material limitations. Do not check acknowledgments on the user's behalf when they require a personal certification the user has not supplied. When a PR is authorized, use a structured body or a body file so prose is preserved accurately.

## 3. Validate and obtain the releasable commit

Use the repository's Make targets and its `venv` tooling. For the Scorecard integration release, [the acceptance checklist](releasing.md#scorecard-integration-acceptance) requires `make check`, `make test-live`, `make test-scorecard`, and `make plugin-validate`, plus the separate Linux Scorecard CI lane. Run board/browser checks when affected or required by current CI. Confirm the selected Scorecard executable and MCP package rather than silently testing a development fork.

Review [integration sessions](../../tests/release-integration.md) and their actual execution records. A manifest validator, tool contract, historical agent rehearsal, or green publishing workflow is not proof of a complete user workflow. Record any unrun release-relevant cases explicitly. Reuse valid evidence for unchanged content; rerun checks when changes or failures invalidate it.

Inspect current required checks, reviews, merge policy, and release environment configuration. Wait for the appropriate checks on the actual candidate. Do not disable a check because it fails on a private repository, waive a ruleset, or use an administrative bypass to manufacture readiness. If a policy exception is requested, explain the concrete failure and handle it as a distinct decision.

When merging is authorized and the requirements are satisfied, use the repository's permitted PR merge flow. Then capture the full merged commit SHA and confirm the relevant checks on that commit; a squash merge can produce a different SHA from the tested branch head. Record this SHA as the release target. Later changes on `main` do not have to be frozen, and they must not silently change the selected target.

## 4. Verify and push the maintainer-supplied tag

Before requesting the maintainer-supplied tag, confirm the target commit contains the intended manifest version and nonempty changelog section, is an ancestor of the fetched default branch, and has the required validation evidence. Check both local and remote tag state again. Supply the maintainer with the exact tag name, full target SHA, release notes, and validation summary.

Once the maintainer-supplied signed annotated tag is available, confirm that it points to the recorded full SHA. Run `tools/release_check.py tag` from a clean checkout of the reviewed default branch, with the current default-branch ref. The checker and allowed public release keys must come from that trusted checkout, not merely from the candidate being checked. Use the checker-generated notes as the expected release text. This routine needs public verification material, not private-key access.

If the tag already exists, compare its tag-object identity and peeled commit with the intended object and remote ref. Resume from a matching verified tag; stop on a conflict. Never move or replace a published tag, even if its workflow failed or no GitHub release exists yet. Resolve any unwanted local-only tag deliberately rather than silently overwriting it.

Once tag verification succeeds and publication is within the user's authorization, push only the exact tag ref. Do not use `--tags`, force-push a tag, or push unrelated branches. If the maintainer already pushed it, inspect the resulting run rather than trying to publish it again. The tag push triggers the existing release workflow; do not race it by creating a second release manually.

## 5. Observe publication and verify

Find the workflow run for the exact tag/commit, not merely the latest successful run. Follow it to completion. If the `release` environment requires a human or independent approval, state the specific pending gate and link the run; do not weaken the environment or represent an agent action as independent human review.

Check the actual GitHub release even if the run fails: publishing can succeed before a later immutability verification fails. Distinguish “tag pushed,” “awaiting approval,” “release published but verification failed,” and “verified release.” Do not rerun a creation step blindly when the release already exists.

Verify the remote tag object, authorized signature, target SHA, manifest version, changelog/release notes, prerelease status, and release immutability using [verification.md](verification.md) and current tool behavior. Reconcile any mismatch before claiming completion. A transient failure may permit rerunning the unchanged workflow; incorrect published content requires a new version, not retagging.

When install verification is in scope, use a disposable client configuration or the user's selected test installation. Check the exact source/ref and installed revision, plugin loading, and relevant MCP connections. Do not uninstall or overwrite the user's working plugin installation merely to make a test clean. Identify whether the install follows `main` or the signed tag; those are different distribution claims.

Conclude with version, full release SHA, tag and release links, verification results, distribution source, and any remaining limitation. If blocked, report the furthest completed state and exact next action instead of saying either “released” or “nothing happened.”

## Resume and private handoff

A new session can reconstruct public release state from Git and GitHub. If useful, keep a short operational record outside tracked files, for example under the local Git metadata directory resolved with `git rev-parse --git-path release-assistant-state.md`. Do not put it under a branch-specific tracked documentation directory. Verify that its resolved location is not a tracked repository path before writing. A worktree may have its own metadata directory; tell the user where the local record lives without copying its contents into a public PR.

Record only what helps resume:

```text
Target version:
Authorized scope and explicit stop points:
Candidate branch / PR:
Candidate SHA / merged release SHA:
Checks and integration evidence (revision-specific):
Tag name / tag-object ID / remote presence:
Workflow run / environment gate:
Release URL / verification state:
Distribution ref / install evidence:
Last completed step / next action:
```

Exclude tokens, passphrases, private keys, sensitive account inventories, and unnecessary environment details. A saved note is context, not new authorization: compare it with the current user request and verify the claimed state before resuming. Do not recommit a version bump, recreate a tag, or republish merely because the previous session ended before its final report.

## Example requests

- “Guide me through preparing the next Badge Buddy beta; don't push anything.”
- “Prepare version X and open its release PR. I'll merge and sign.”
- “Handle the release of version X autonomously: prepare its PR, merge when permitted, and publish and verify the signed tag I supply. Tell me if a required approval needs me.”
- “Resume the release of version X. Inspect the existing PR, tag, and workflow before doing anything new.”

Replace X with the intended version. None of these examples is an instruction to execute a release merely because this document was read.

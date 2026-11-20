# Integration sessions for the Scorecard release

Prepared 2026-11-20. This is a plan and release decision aid, not a record of additional executions. Use it alongside the [release procedure](../docs/release/releasing.md), [badge evaluations](badge-skill-evals.md), and [Scorecard evaluations](scorecard-skill-evals.md).

## Release scope

Validate the Badge Buddy candidate with its pinned Best Practices MCP and the documented upstream Scorecard 5.7.0 executable. The Scorecard fork, hosted Cloudflare service, new fork tools, and hosted authentication are separate tracks. They are not dependencies of this release and must not accidentally substitute for the upstream binary during acceptance testing.

Use a fixed candidate revision and the actual plugin installation path. Record any later skill edits and rerun the affected scenario on the resulting revision. A passing conversation against an earlier prompt is not validation of the final instructions. Keep the larger model-comparison harness in parallel; its completion is not a release prerequisite.

## What has already run

- Claude Code 2.1.327 on macOS arm64 loaded a disposable local marketplace. Connection checks covered both MCPs, PATH selection, an absolute executable override, missing/empty/old executable cases, and restart after repair. These used the plugin's actual registration.
- Three Best Practices agent sessions on 2026-11-19 exercised resume/wording preservation with hostile saved evidence, transfer of a selected answer, and reset to unknown. They used a fixture MCP and a plugin copy without production registration. Peer review, previews, and website saving were deliberately excluded.
- Thirteen Scorecard development sessions on 2026-11-20 used explicit invocation and controlled REST evidence through the real upstream MCP. The record preserves permission-confounded attempts, targeted reruns, and remaining explanatory mistakes. The successful behavioral sessions were not a complete install-to-finish production workflow.
- Automated tests exercise real binaries, contracts, snapshots, partial scans, and isolated draft operations. A separate direct remote CLI License scan succeeded. Neither demonstrates that an agent can conduct the entire real workflow.

The records identify the client-reported model as `claude-opus-5-5`. These are observations of specific sessions, not an Opus/Sonnet comparison or a model reliability estimate. See the linked execution artifacts before interpreting a scenario as passed. No additional Claude sessions were started while preparing this checklist.

## Suggested next sessions

Start with the first three sessions. Then use short focused cases for the remaining high-risk boundaries instead of repeating a full application every time. For a new beta, require a credible successful primary workflow for each skill and resolution of material failures; explicitly record which secondary cases remain deferred.

| Session | Natural user task | What to observe |
| --- | --- | --- |
| Installation and coexistence | Install the candidate through the intended marketplace/local test channel; “Help me understand this repository's Scorecard results.” Then ask a Best Practices question. | Confirm exact plugin revision, qualified tool names, actual resolved binary/build, both server statuses, and correct skill selection. Use a fresh session without pasted skill instructions. Add explicit invocation as a separate case if automatic selection fails. A zero exit from `mcp list` does not prove both servers connected. |
| Best Practices application and review | “Help me complete the Passing application for this registered project using the facts I provide.” | Verify project association, synchronization, criteria interpretation, truthful treatment of missing facts, useful questions, a real second-agent review, and incorporation of corrections. Capture the draft before/after review and the reviewer's identity/context. The review evaluates the agent's contribution, not the maintainer's honesty or entitlement to a badge. |
| Scorecard diagnosis and planning | “Explain the most useful improvements for this repository; investigate one confusing check and give me a realistic plan.” | Read published evidence through MCP, inspect the measured revision, investigate the detector where necessary, and propose a small actionable plan. Distinguish benefits, expected recognition, measured effects, and history-dependent work. A large score increase in one session is not the success criterion. |
| Best Practices resume and transfer | Stop and reopen the application session; revise one answer, preview it, cancel one undecided edit, and prepare only the requested changes for the website. | Preserve durable drafts, resolve site/draft differences intentionally, discard canceled wording, keep answer/status pairs together, and explain what is saved where. If a real save is explicitly authorized, check the website afterward and synchronize in a new session. A proposal URL alone is not a saved update. |
| Scorecard targeted diagnostic | “Will this modest fuzzing setup count? Run only the relevant supported checks and explain the evidence.” | Use the same executable as MCP, preserve a fresh report, inspect exit status and output together, and research version-specific recognition. Distinguish local detection from remote language selection and public measurement. Do not promise a score change. A useful small score-motivated improvement is acceptable. |
| Scorecard evidence and follow-up | Supply partial/incompatible reports; then show a green publication run whose public result still names an older commit. | Preserve useful per-check evidence, withhold unsupported aggregate deltas, and report publication pending. Provide a concrete next observation without fabricating reviews, merges, historical activity, or a new score. A fixture is appropriate for the stale-publication case; an actual publication exercise is optional and separately scoped. |

For the application session, Badge Buddy itself is a possible real project if the maintainer chooses to start its application. That choice is not made by this document. Registration, remote edits, proposal saving, and implementation/publication work need the user's actual intended scope. Use ordinary tools and realistic permissions for attended sessions; keep destructive/recovery and hostile-data cases in disposable fixtures. Redact credentials before retaining transcripts.

## Focused checks and questions

### Best Practices

- Does a user-supplied fact lead to a faithful answer without unnecessary skepticism or unsupported embellishment? Does an unknown remain a question rather than become an invented fact?
- Does the reviewer actually run, receive the complete relevant criterion and user context, and improve the author's work? If unavailable or explicitly skipped, is that limitation disclosed?
- Do preview cancellation, status-only/wording-only changes, session restart, and conflicting saved answers preserve the intended state?
- Are oversized proposals split without dropping answers or truncating justifications? Is the website's inability to reset an answer through a proposed `?` explained accurately?
- Does an uncertain update trigger a read before retry? Does hostile project text remain evidence when handed to the reviewer?
- The current skill still documents pre-registration answer files. Decide whether that path belongs in the advertised release scope; if retained, exercise its actual storage and later registration handoff. Do not assume that discussion of de-emphasizing the path removed it from the implementation.

### Scorecard

- Explain absent, inconclusive, zero, and truncated results separately. Detail-line counts must not become counts of distinct defects; this failed in an earlier rehearsal.
- Diagnose an unavailable MCP from actual configuration. Do not infer an executable named `stdio` from a host error label; this also failed earlier. Do not introduce a redundant script query fallback.
- Keep installed engine identity separate from the engine in a published report. Explain any compatibility claim using the tested baseline, not an untested “or later” promise.
- A nonzero CLI exit may retain valid partial evidence. Missing/malformed new output must not cause an old report to be reused. The controller does not calculate upstream scores.
- Matching commits do not imply unchanged settings/history; different version labels alone do not establish fabricated evidence. Explain why particular comparisons are or are not defensible.
- Missing published data should lead to a choice of useful next work, not automatic installation of a publication workflow. Cached reads should not request a GitHub credential.
- Inspect exact detector behavior for the selected check/version when it matters. Classify recommendations as source-supported, locally observed, remotely observed, or uncertain; do not grade eloquence as correctness.
- If GitLab subgroup support is advertised, exercise its explicit capture/import exception independently. Do not generalize it into a fallback for ordinary MCP failures.

### Boundaries between skills

Test a Scorecard `CII-Best-Practices` finding that leads to application work, and a Scorecard workflow/SAST/coverage recommendation that uses an adjacent skill. The handoff must preserve repository identity, evidence, and the user's scope; it must not merge the two products' scores or imply one badge guarantees another. Missing Scorecard must not prevent Best Practices work.

## Establish a baseline without pretending one already exists

Use a real public repository with a current published result for the main Scorecard session, plus a disposable repository or supplied snapshots for controlled failures. Before the agent run, independently inspect a small selected set of checks against upstream output and detector source. Record expected facts and explicitly uncertain predictions; do not manufacture an oracle for every possible recommendation.

Retain the first unassisted attempt, including mistakes. If guidance changes, record a new attempt rather than replacing the failed transcript. One realistic Opus session and one Sonnet session on the same final candidate would provide useful exploratory evidence; they would not establish comparative reliability. The planned harness can later add repeatable fixtures, independent attempts, configurable author/reviewer pairs, and contamination controls.

## Execution record and release decision

For each session record candidate SHA, installation source, host/model IDs, MCP/executable versions and paths, repository revision, relevant remote settings, exact prompt, enabled tools/permissions, credential access scope without values, tool-call artifacts, reviewer activity, user interventions, results, cost/time, and unresolved concerns. Separate installation failures, model mistakes, fixture defects, and implementation defects. Save enough evidence to reproduce the finding without retaining secrets or unrelated private material.

Before merging/tagging, review these sessions and run the existing release checks, including the separate Linux Scorecard CI lane. Confirm the candidate inventory and release notes describe the required executable and command changes. Harmful state loss, fabricated measurements, credential exposure, and broken primary workflows require correction and affected-case reruns; cosmetic or secondary limitations can be documented explicitly for a beta.

Confirm the distribution decision before merging: the documented marketplace currently follows `main`, so merging can expose new plugin content before tagging. Either knowingly retain that beta behavior or arrange the intended release reference first. Rehearse installation from the chosen source and verify the exact revision received. This is a concrete distribution check, separate from the larger signing/verifier research.

The larger [Passing benchmark](../docs/plans/badge-application-evaluation.md) and [evaluation-methodology research](../docs/research/skill-evaluation-methodology.md) remain parallel work. They should reuse useful scenarios and traces from these sessions while keeping development examples separate from later held-out evaluations.

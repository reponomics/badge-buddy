# Scorecard CLI and MCP integration plan

## Amendment: agent-guided verification without snapshot management (2026-11-21)

Status: implemented for the pending v0.5.0 release. The controller has been removed and active guidance follows the MCP/CLI and ordinary-host procedures below. Deterministic contracts and attended behavioral smoke tests remain distinct release checks; see the [release acceptance checklist](../release/releasing.md#scorecard-integration-acceptance). This amendment supersedes the snapshot retention, controller parity, mandatory report saving, and offline controller requirements in the historical plan below, including the corresponding validation gates. It does not change the release version or authorize publication.

### Decision

The Scorecard evidence controller (`scripts/scorecard.py`) and its `fetch`, `explain`, and `diff` entry points are retired. Do not retain a backup query path or replace it with another storage/comparison wrapper. The skill should describe procedures that an agent can follow using upstream MCP tools, direct Scorecard CLI diagnostics, and ordinary host tools. Reading user-supplied JSON and comparing historical measurements remain supported activities; neither requires a plugin-owned persistence mechanism.

Saving a report is optional. When requested, the agent can save upstream JSON to a user-chosen destination using the host's ordinary tools and permissions. Do not require a baseline file, storage directory, filesystem grant, or automatic archive as a prerequisite for Scorecard assistance. Temporary output needed for a particular CLI invocation is an implementation detail, not a durable snapshot workflow. Do not automatically save every result.

### Procedure to teach

1. Follow the user's question and scope. Use the upstream overview, then request details only for relevant checks; consult truncation metadata and increase `max_details` within its supported limit when needed. Use the CLI for requested fresh diagnostics or supported local checks.
2. Investigate the relevant scanner version's recognition rules and propose or implement the selected change within the user's authorization. The verification objective is whether Scorecard recognizes the change; a separate assessment of the practice's broader effectiveness is not a prerequisite.
3. After the relevant merge and subsequent measurement, inspect the new result. For historical comparisons, query MCP with each target repository commit SHA where published measurements are available, then request selected-check details as needed. This route requires neither GitHub access nor full-report export. If MCP evidence is unavailable or insufficient, inspect a previous workflow report using ordinary host tools: prefer an uploaded JSON report when available, then logs that contain useful results. Logs may omit or truncate the report, and neither source guarantees all checks ran. User-supplied evidence remains usable. Do not add a GitHub client or credential store to the Scorecard MCP for this purpose.
4. Identify the repository, measured commit/date, scanner build, check coverage, and source of each result. Explain per-check changes and reported overall scores where comparable. Preserve the distinction between zero, absent, and inconclusive results. Do not recompute an aggregate or treat a selected diagnostic as a full published measurement.
5. Link the measurements used. If older evidence is unavailable or the log does not contain a report, say so and use available evidence; do not invent a baseline or require the user to have saved one earlier. Save JSON only when requested or otherwise authorized for the task.

A successful workflow and a changed public API result are separate observations. When the question concerns a badge update, verify the published measurement as well. Historical logs are subject to retention, and report content varies by workflow; neither limitation makes persistent plugin-managed snapshots a default requirement.

### Use existing MCP measurement metadata

The existing MCP result already supplies the measurement context needed for agent-guided comparison: `repo`, target repository `commit`, measurement `date`, `scorecard.version` and `scorecard.commit`, `source`, reported `score`, per-check scores/reasons, `caveats`, `missing_checks`, and `complete`. Use those fields directly; do not introduce a plugin metadata format, provenance sidecar, or an MCP feature solely to reproduce them. The target repository commit and the scanner build commit identify different things and must not be confused.

`missing_checks` is calculated from the catalog bundled with the running MCP server: it lists expected non-experimental checks for the repository platform absent from the result. It does not reconstruct the historical scanner's catalog. `complete: true` means those expected check names are present, not that all scores are conclusive or every detail is returned. Compare the actual check sets and scores as well as metadata; an incomplete result can still support comparison of individual checks present in both measurements. Missing and inconclusive results are not zero. A transition from `-1` to a numerical score is newly conclusive evidence, not a numerical gain from `-1`. Explain material differences in scanner build, source, coverage, and measurement conditions. Distinguish an observed change from a claim that a particular edit caused it; no custom comparison engine is required.

Complete raw-report retrieval is a separate question about omitted detail, annotations, or original fields; it is not needed to obtain the measurement identity and completeness metadata above. Existing metadata support strengthens the case for removing the custom snapshot layer.

### Upstream design context

The following decisions were verified in upstream's `v5.7.0` history, separately from fork additions. Read them before changing tool boundaries; compact output is intentional, not evidence of an unfinished full-report interface.

- [Original design, D4 and D5](https://github.com/ossf/scorecard/blob/v5.7.0/openspec/changes/archive/2026-08-04-add-scorecard-mcp-server/design.md): commit-specific retrieval and measurement metadata support downstream historical reuse; consumer caching belongs to the consumer. The five-tool interface deliberately offers compact overviews followed by selected-check detail to manage context size.
- [Design audit and authoritative resolutions](https://github.com/ossf/scorecard/blob/v5.7.0/docs/design/mcp-design-audit.md#resolutions): F7 rejected `details:false` because it conflicts with the detail tool's purpose. It chose `max_details` (default 50, cap 500) with `details_total` and `details_truncated`, informed by live samples reaching 377 entries. Truncation is applied in the handler, not the provider. Increase the supported detail limit when useful before seeking another evidence source.
- [Integration review fixes](https://github.com/ossf/scorecard/blob/v5.7.0/openspec/changes/add-mcp-subcommand/tasks.md#4-review-fixes): missing-check calculation, provenance, completeness, and attribution were explicitly reviewed. Reuse them rather than introducing parallel metadata.
- The audit's D1 resolution deliberately selected stdio and in-tree distribution; Directory submission was not a current goal. The transport-independent factory and [published roadmap](https://github.com/ossf/scorecard/blob/v5.7.0/docs/mcp.md#roadmap) allow HTTP as an independent extension. Live scanning was deferred for separate decisions on authentication, lifetime, progress/cancellation, and tool surface.

The audit records source and SDK inspection, real stdio probes, live API calls, and decisions resolved individually. This is documented project rationale, not a claim that this amendment independently repeated that validation. Future proposals should identify a concrete unmet task and explain why existing tools and ordinary client procedures do not suffice.

### Implementation and acceptance

- Remove the controller, its skill permissions, command examples, and tests that exist solely to preserve its interfaces. Update callers, README, references, packaging, and test/build configuration as necessary. Keep meaningful upstream MCP/CLI contract coverage and review remaining coverage requirements after deleting obsolete code.
- Replace controller-based inspection in live-CLI tests with direct assertions against upstream JSON. Preserve coverage for useful partial output after a nonzero exit, missing or malformed output, and stale-result avoidance; remove tests only when they solely enforce the retired controller interface.
- Replace snapshot-first skill instructions with the procedure above. Inspect supplied JSON directly with ordinary host capabilities; there is no plugin-specific import format or required provenance sidecar.
- Remove the controller-based GitLab subgroup workaround. State the upstream MCP limitation and allow ordinary investigation of available published evidence within the user's scope; do not promise identical platform support or silently substitute a second backend.
- Verify a current-status request, a selected-check investigation, commit-specific MCP comparison, historical workflow-report comparison when MCP evidence is unavailable or insufficient, supplied JSON, an unavailable baseline, differing scanner/check coverage, and an optional user-requested save. Verify that ordinary queries and comparisons do not automatically write reports. Keep execution records private under repository guidance.
- Keep the installed CLI and upstream MCP integration, direct diagnostic support, partial-result handling, and publication procedures. No Best Practices draft-storage changes are included.

### Review and implementation handoff

A separate review supplied on 2026-11-21 recommended proceeding with these clarifications. It covered plans and relevant implementation, not runtime testing. Its findings are incorporated above: overview/detail routing, commit-specific historical queries, workflow-report alternatives, comparison safeguards, catalog-relative completeness, and preservation of meaningful CLI tests. The accompanying fork amendment addresses the residual snapshot-based HTTP request-size rationale and independent contribution scopes.

Before editing, inspect the current branch and worktree; this amendment is not evidence that the release branch remains at its historical state. Audit all controller callers, permissions, mandatory-save instructions, and helper-dependent tests. Implement the plugin cleanup as a focused changeset, run appropriate remaining checks, and report actual validation. Do not publish transcripts or treat this design review as runtime acceptance. This is a Scorecard change only; Best Practices persistence is outside scope.

## Historical plan and implementation record

Status: implemented locally on 2026-11-20 under proposed version `0.5.0-beta.1`; on 2026-11-21 the maintainer requested release as `0.5.0`, prepared on `codex/release-0.5.0`. The approved plan below was recorded and reviewed on `codex/scorecard-cli-mcp-plan`, based on Badge Buddy commit `62d49824458051e6ffb0ed0c14ed27cdc5d4acd1`. Historical evaluation records retain the version actually tested.

The initial implementation included the required Scorecard MCP registration, same-executable CLI guidance, capture-only `fetch --output`, retained offline evidence operations, and an independent verified-binary CI lane. The amendment above supersedes its controller and persistence requirements; the material below is historical context, not active plugin guidance. See [Scorecard evaluation scenarios](../../tests/scorecard-skill-evals.md) for the behavioral and host checks; execution records remain private. The release acceptance checklist remains in [Releasing](../release/releasing.md#scorecard-integration-acceptance). The historical baseline and implementation gates below explain the decisions; they are not a claim that every platform or behavioral scenario has passed.

Related private planning lives in the sibling Scorecard fork on `badge-buddy-integration`, under `planning/badge-buddy/` (initial planning commit `5d418dfb`). That work covers the hosted service, provider research, and upstream contributions. This document is the implementation plan for the Badge Buddy side and must remain usable without that checkout.

## Intended result

Make upstream Scorecard the primary interface for reading and explaining published results and for running diagnostics. Use the MCP for its supported queries and explanations, and the same installed binary's CLI for fresh selected scans and local file checks. Preserve the controller's useful evidence-handling capabilities until upstream can replace them without loss.

This is a selective replacement of controller-driven interaction, not a requirement to remove every script. It should give maintainers more capability while reducing duplicated integration logic. The first integration release uses a user-installed Scorecard executable; hosted MCP development proceeds independently and does not block it.

The Scorecard binary is a required dependency for the integrated Scorecard workflow, not an optional advanced diagnostic tool. Its MCP subcommand and scanning CLI are both supported first-class interfaces. Conceptual discussion and reading already supplied evidence can proceed without running it; these primitive operations do not constitute an alternative backend. Other Badge Buddy skills do not acquire a Scorecard prerequisite merely by being in the same plugin.

Do not maintain redundant script implementations as connection-failure backups. Retained scripts must provide capabilities absent from the upstream interfaces: original published snapshots, supplied-document inspection, and provenance-aware comparison. Remove the redundant live-query command mode in this integration rather than leaving it indefinitely deprecated.

## Pre-integration baseline

- [.mcp.json](../../.mcp.json) starts only `bestpractices`, using `best-practices-mcp==0.7.0` through `uvx`.
- [The Scorecard skill](../../skills/ossf-scorecard/SKILL.md) uses `scripts/scorecard.py` (now removed) for `fetch`, `explain`, and `diff`. Its tool permissions reference that controller. It explicitly says the plugin does not install or orchestrate Scorecard binaries.
- The controller reads public API results without credentials, imports upstream JSON, saves original documents with acquisition provenance, and compares snapshots conservatively. It does not scan repositories.
- [Authentication and results guidance](../../skills/ossf-scorecard/references/authentication-and-results.md) treats CLI diagnostics as an already established user workflow. [Publication guidance](../../skills/ossf-scorecard/references/action-publication.md) distinguishes diagnostics from public results.
- Controller tests (`tests/test_scorecard.py`, now removed), [documentation integrity tests](../../tests/test_documentation_integrity.py), [engineering evaluations](../../tests/engineering-skill-evals.md), README text, and CI checks encode aspects of this behavior.

## Upstream baseline and boundaries

Use v5.7.0 as the first tested compatibility baseline; confirm its distribution and contracts in the first implementation gate. Newer builds are not automatically considered tested, and no older build is supported without explicit validation. `scorecard mcp` ships inside the full Scorecard binary. The released MCP uses stdio and reads precomputed public results; it does not execute scans. Installing the binary locally makes the CLI available to an agent with shell access, but does not make CLI operations callable through MCP.

The five tools are `get_repo_score`, `get_check_result`, `compare_repos`, `list_checks`, and `explain_check`. `compare_repos` compares different repositories, not saved before/after evidence. Repository responses summarize checks; single-check responses default to 50 detail entries and cap them at 500. The provider also projects upstream JSON into selected fields, so removing that cap alone would not make exports lossless.

The CLI supports selected remote checks, supported local file checks, detailed JSON, annotations, and probe output. Remote scans need suitable credentials. Conventional JSON is a report, not every internal observation. Feature-gated raw/probe capabilities should not become first-release dependencies without separate validation.

Sources: [MCP documentation](https://github.com/ossf/scorecard/blob/v5.7.0/docs/mcp.md), [MCP result implementation](https://github.com/ossf/scorecard/blob/v5.7.0/cmd/internal/mcp/server/tools_results.go), [CLI options](https://github.com/ossf/scorecard/blob/v5.7.0/options/flags.go), [JSON serialization](https://github.com/ossf/scorecard/blob/v5.7.0/pkg/scorecard/json.go).

## Responsibility split

| Operation | Initial implementation | Reason |
| --- | --- | --- |
| Read a published overview or individual check | Upstream MCP | Standard supported tool interface with measurement provenance |
| Explain a check's general methodology | Upstream MCP, followed by version-specific source research as needed | Avoid maintaining another catalog; bundled docs are not a patch prediction engine |
| Run a fresh selected remote check | Direct upstream CLI invocation | Available in the installed binary; not exposed by the current MCP |
| Check relevant uncommitted files | Direct upstream CLI invocation where supported | Useful preflight without implying remote settings/history were checked |
| Save a fresh diagnostic result | CLI JSON output | Preserve the emitted report, details, annotations, and scanner identity |
| Save an original published baseline | Retain controller `fetch`, with `--output` required | MCP summaries cannot reconstruct all upstream evidence; eliminate the query-only mode |
| Inspect supplied JSON | Retain controller `explain --input` as a file/stdin operation only | Upstream MCP cannot import a supplied result; this is document inspection, not a competing check catalog or live query |
| Compare saved results | Retain controller `diff` | Neither current MCP nor supported public CLI replaces the provenance checks |
| Configure publication and verify badge update | Existing publication procedure | Fresh diagnostics do not publish to the public API |

Avoid duplicate routine acquisition: use MCP for conversational queries; use the controller when an original published snapshot is required. If both are used, compare target commit, measurement date, and scanner identity before treating them as the same measurement. The latest public result can change between calls.

Explicit platform exception: the inspected upstream MCP parser rejects GitLab subgroup paths, while our controller supports their published records. Preserve that capability through explicit snapshot capture followed by supplied-document inspection, with an output path and a stated MCP limitation. This is additive support for a missing upstream operation, not a connection-failure fallback. Test subgroup capture/import separately from ordinary MCP routing and do not route it into GitHub Action setup. Recheck the limitation at the selected release before documenting it.

## Proposed changes, in implementation order

### 1. Rehearse installation and define the supported configuration

Document user installation from upstream's supported release distribution. The plugin should declare a `scorecard` MCP entry equivalent to `command: scorecard` with `args: [mcp]`; preserve the existing Best Practices entry. Rehearse PATH discovery in an actual plugin host and document the supported absolute-path override mechanism before relying on it.

Select one resolved Scorecard executable for both MCP startup and direct CLI commands. Record its version/build and verify the host configuration and shell resolve to that executable; a GUI PATH and an interactive shell PATH may differ. If an absolute-path override is used, CLI diagnostics must use that same executable. Include an intentional two-binary/PATH mismatch rehearsal and diagnose it rather than silently accepting different scanner builds. Do not confuse the installed build with the scanner build reported in a historical published result.

Record the tested Scorecard version and platforms. Distinguish a minimum supported version from an exact runtime pin: a PATH-resolved user binary is not pinned merely because documentation names a version. Choose a compatibility policy and report the observed version when diagnosing behavior. CI should use an exact tested release with artifact verification appropriate to upstream distribution.

Do not add committed binaries, automatic downloads, installer hooks, global PATH modification, or a custom MCP client in this pass. Do not reuse the Python `requirements-mcp.txt` pin mechanism for a Go executable. Confirm that a missing required Scorecard executable is diagnosed for the Scorecard workflow without preventing use of other skills; if the host handles this poorly, resolve the configuration strategy before release.

Acceptance: a clean setup connects; missing/old executables produce actionable instructions; ordinary published queries require no GitHub token; existing Best Practices behavior remains functional.

### 2. Update skill orchestration and permissions

Replace controller-first routine queries with MCP operations. Update the skill's entry paths, frontmatter permissions, and reference documents to reflect direct CLI diagnostics. Validate actual plugin-qualified MCP tool names and host permission syntax; do not guess them or grant broad shell access merely for convenience.

Keep the durable skill focused on when to use each interface, how to select the target repository/checks, and how to interpret evidence. Let upstream tool schemas describe parameters. Put installation, version troubleshooting, CLI examples, and evidence details in focused references rather than duplicating long descriptions in the skill.

If MCP is unavailable, diagnose the connection without silently installing software or routing routine queries through the controller. Supplied-document inspection remains independently useful, and snapshot capture remains an explicitly requested evidence operation; neither is a replacement query backend. Lack of a published result should offer a fresh diagnostic when appropriate, not automatically install an Action or demand publication. Preserve GitLab record/import support without implying parity for every scan or publication workflow.

### 3. Add deliberate CLI diagnostic workflows

Teach two explicit paths: a targeted remote scan for fresh repository evidence, and local file preflight for checks supported by `--local`. Select relevant checks rather than running every check for a narrow question. Use the project's actual directory, quote paths, and select a new output path without overwriting the baseline. Save requested details and annotations; use debug verbosity when the investigation needs details filtered at the default level.

Record the command's scope, target, installed scanner build, result commit/date, credentials' relevant access limitations, and whether the result is local, remote diagnostic, or published. Record no secret values. Inspect exit status and result availability together: a scan may fail some checks while leaving useful evidence. Verify exact behavior against the selected release and preserve usable partial results with clear limitations.

For this first pass, record command/scope/access context in the diagnostic handoff or user-requested work log alongside the output path; do not invent a new provenance writer or schema. Bare CLI reports remain generic imports in the existing controller. Its checks establish structural comparability, not credential equality or equivalence of invocation conditions. If those conditions are unknown, explain the limitation even if the structural diff permits a delta.

Require two failure-path evaluations: nonzero exit with a valid newly produced report retains useful partial diagnostics, and nonzero exit with absent or malformed output is reported as a failed measurement. Use a fresh destination so an older report cannot be mistaken for a new scan. Neither case warrants adding a custom CLI execution wrapper.

Keep credentials in the user's environment or normal secret tooling. Cached public queries do not need a token; remote diagnostics may. Diagnose the specific permission gap before broadening access. For publication use the existing Action authentication procedure. Do not create or publish workflows just to make a diagnostic run possible.

Acceptance: the agent can run a fresh selected check and explain its JSON, perform a supported local preflight, and distinguish both from public badge verification. Do not add a Python execution wrapper unless a concrete orchestration need emerges that direct CLI use cannot reasonably satisfy.

### 4. Retain additive evidence operations and remove redundant paths

Require `--output` for `fetch`, removing its query-only form. Keep the network/serialization code needed to capture the original API document; that transport is necessary for a unique capability, not a redundant fallback product. Limit its command response to capture confirmation and provenance needed to identify the saved result rather than maintaining another live findings interface. Keep `explain --input` for normalized inspection of supplied file/stdin evidence and keep `diff` for comparisons. Do not add network lookup or scanner orchestration to either operation.

Update every caller, example, parser test, and evaluation affected by the required output argument and narrowed capture response. Remove obsolete assertions rather than preserving the old command contract as a compatibility fallback. Describe the command change and required Scorecard dependency in the changelog. Preserve tests for parsing, acquisition failures, snapshot fidelity, imports, and comparisons that still support the retained operations. No command rename or general controller refactor is required.

Preserve upstream annotations and unknown fields in original snapshots. Do not feed MCP summaries or controller interpretation output into a path expecting a saved original report. Distinguish check absence, inconclusive status, and interface truncation. An incomplete result is not necessarily unusable.

Keep comparison safeguards for repository identity, scanner version/commit, source, check coverage, inconclusive-state changes, and chronology. A fresh scan of a selected subset is not interchangeable with a full published scan; even two complete reports can differ in credentials or engine behavior. Explain why an aggregate delta is withheld while retaining useful per-check observations.

### 5. Revise remediation and planning guidance

Explicitly allow score-motivated incremental improvements. Replace the playbook's categorical preference against projected score lift with guidance that considers user goals, usefulness, effort, maintenance, and likely detector recognition together. A small real implementation can be worthwhile; it need not be a project's highest-priority security investment.

Use the Atheris case as a behavioral example: investigate how the relevant scanner version recognizes Python fuzzing, add a modest useful target, exercise it, preflight where supported, then verify a later remote result. Local and remote Fuzzing language selection differ, so a local success is not a guarantee of remote detection. The skill should permit ordinary upstream source inspection without maintaining its own detector implementation.

Distinguish implementation value, expected recognition, and observed score effect. Do not invent practices, reviews, contributors, or releases. Keep longitudinal work explicit: proposed, implementing, PR open, reviewed, merged, awaiting measurement, observed. A Markdown plan is sufficient when useful; no new persistence subsystem is required. History-dependent checks should lead to realistic follow-up work rather than promises of a large score increase in one session.

### 6. Document, evaluate, and prepare a release proposal

Update README installation and Scorecard sections, the three Scorecard references, skill permissions/instructions, contribution/test guidance where affected, and behavioral evaluations. Preserve the independent Best Practices workflow and terminology. Add an Unreleased changelog entry when implementation changes user behavior; select a release version through the normal release process, not in this planning commit.

The implementation PR must include a plugin version bump and changelog coverage for the required dependency and retired query-only command. The current `tools/release_check.py` pin-bump gate watches `requirements-mcp.txt`, so it covers the Best Practices package, not a PATH-resolved Scorecard executable or its compatibility policy. Keep that gate's scope explicit in contribution/release guidance and add a release acceptance check for the Scorecard integration/version change; do not claim existing automation enforces it. A generalized dependency gate is not required for this first pass.

Audit release packaging and validation so any added documentation/configuration is included intentionally. A successful manifest validator does not prove executable availability, connection behavior, or tool correctness. Keep those checks distinct. Do not tag, publish, push, or configure a hosted endpoint as part of implementing this plan unless separately requested.

## Validation plan

| Layer | Required evidence |
| --- | --- |
| Offline regression | Retained parsing/snapshot/diff cases pass; query-only `fetch` is rejected and snapshot capture has the documented response |
| Evidence fidelity | Original documents retain annotations/unknown fields; capped MCP results never masquerade as complete snapshots |
| Comparison behavior | Mismatched engines, sources, check sets, inconclusive results, chronology, and same-commit measurements remain explicit |
| Platform compatibility | GitLab subgroup snapshot/import remains supported with the MCP limitation explicit; no silent fallback for supported MCP queries |
| Documentation integrity | Command examples, references, permissions, and MCP configuration agree with actual interfaces |
| Upstream contract | Real selected Scorecard binary initializes and serves catalog/explanation tools; controlled REST responses exercise query/error/truncation paths |
| CLI integration | A disposable fixture exercises supported local scanning/import; nonzero exit with valid partial output and absent/malformed output are evaluated without reusing stale files |
| Actual host | Fresh plugin installation, PATH discovery, missing binary, intentional MCP/CLI executable mismatch, tool naming, coexistence with Best Practices, and connection restart |
| Behavioral evaluation | Published diagnosis uses MCP; a missing binary/server leads to setup/connection diagnosis rather than scripted query fallback; no published result, narrow fresh scan, local fuzzing preflight, supplied partial JSON, incompatible comparison, and post-merge verification are exercised |

Keep ordinary tests offline and retain subprocess coverage aggregation and both coverage floors. Separate tests needing the real Scorecard executable/network from `make test`. Add a dedicated Scorecard contract/CLI Make target with a configurable `SCORECARD` executable variable and a separate CI job; both are first-release requirements. Use the real pinned test binary with controlled REST responses and a disposable local fixture so results do not depend on live public repository scores. Verify the downloaded artifact and report the tested build. Do not make unrelated Best Practices contract tests depend on Scorecard. Use existing `venv` tooling for Python tests.

During implementation run focused checks and then `make check`, the relevant real-server contracts, and `make plugin-validate` when available. Record actual host/skill evaluations separately from unexecuted scenarios. CI changes must use SHA-pinned actions, minimal read-only top-level permissions, and job-scoped elevations only when needed. Resolve exact versions and SHAs at implementation time.

## Suggested commit boundaries

1. MCP configuration, supported-installation documentation, and connection/contract validation.
2. Skill MCP/CLI routing, permission changes, and relevant behavioral/documentation checks.
3. Remove query-only fetch, narrow capture output, and retain additive evidence operations, with regression coverage and caller updates in the same commit.
4. Remediation and longitudinal planning guidance with recorded evaluations.
5. Release-facing documentation/changelog and any coordinated version change when ready.

Keep each commit coherent and passing; combine dependent documentation/tests with the behavior they verify. These boundaries are guidance, not a reason to leave stale instructions temporarily active.

## Hosted transition contract

The Scorecard fork owns HTTP transport, service deployment, and proposed export/comparison/live-scan tools. Badge Buddy owns installation guidance, skill orchestration, and user workflows. The local integration must not wait for the hosted track.

A hosted binary does not give the client shell access to the CLI. Only exposed server tools become remotely available. The local binary remains required under this first-release contract. A future hosted release may revisit that requirement only after defining which capabilities the service replaces and which still require local execution; transport support alone does not justify making the CLI optional. Do not promise local workspace inspection over HTTP or silently upload source. Introduce an experimental channel only when it helps real testing; avoid a permanent duplicate skill codebase.

When upstream or the fork offers complete exports/comparisons, reassess the retained controller through the same parity tests. Transport changes alone are not grounds to remove it. Coordinate live scanning with [upstream issue #5413](https://github.com/ossf/scorecard/issues/5413); HTTP is also on the [MCP roadmap](https://github.com/ossf/scorecard/blob/v5.7.0/docs/mcp.md#roadmap).

## Decisions to resolve during implementation

- Confirm the v5.7.0 baseline on the intended platform matrix and document incompatibility diagnosis without a custom launcher; this is gate 1, before skill migration.
- Host-supported absolute-path override and behavior when Scorecard is absent, including impact on other skills.
- Exact MCP tool permission declarations and the narrowest practical CLI permission policy.
- Resolve the verified artifact acquisition details for the required independent Scorecard contract/CLI CI job.
- Whether additional controller code becomes unused after removal of query-only fetch; remove dead code without broad unrelated refactoring.
- Which behavioral scenarios have been run successfully enough to support the first integration release.

No hosting provider, public endpoint, install automation, or release date is selected by this plan.

## Review record

Two independent agent reviews examined implementation readiness and evidence/migration behavior against the existing Badge Buddy code, tests, release tooling, and relevant Scorecard source. Both reviewers re-read the revised plan and reported no remaining blocking findings. This is a plan review, not a claim that runtime behavior has been tested.

| Finding | Resolution incorporated in this plan |
| --- | --- |
| Optional dependency and connection-failure fallback language conflicted with intended direction | Required binary for integrated Scorecard work; no redundant query backend; primitive discussion/import operations remain available |
| Retaining all commands left duplicate querying in place | Require capture output, narrow capture response, reject query-only fetch; retain supplied-document inspection and comparison |
| GUI and shell could resolve different executable builds | Select one resolved executable for both interfaces and test an intentional mismatch |
| Existing release guard only covers the Best Practices pin | Require integration version/changelog updates and an explicit release acceptance check; document the guard's actual scope |
| Upstream MCP rejects GitLab subgroup paths supported by our controller | Preserve explicit subgroup snapshot/import as additive functionality and evaluate that route |
| Successful local fixture did not cover partial scan failures | Require nonzero-exit cases with valid partial output and absent/malformed output; prevent stale-result reuse |
| CLI output does not capture all invocation/credential context | Record context in the diagnostic handoff and state structural comparison limits; no new provenance subsystem |

The reviews also tightened the first tested version baseline and made the separate Scorecard contract/CLI CI lane a first-release requirement. Installation/host validation and verified artifact acquisition remain implementation gates, not reasons to defer the entire integration or start the hosted track first.

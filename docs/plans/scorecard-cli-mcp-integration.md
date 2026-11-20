# Scorecard CLI and MCP integration plan

Status: proposed implementation plan; no runtime changes yet. Recorded 2026-11-20 on `codex/scorecard-cli-mcp-plan`, based on Badge Buddy commit `62d49824458051e6ffb0ed0c14ed27cdc5d4acd1`. Keep this branch local until the maintainer requests publication.

Related private planning lives in the sibling Scorecard fork on `badge-buddy-integration`, under `planning/badge-buddy/` (initial planning commit `5d418dfb`). That work covers the hosted service, provider research, and upstream contributions. This document is the implementation plan for the Badge Buddy side and must remain usable without that checkout.

## Intended result

Make upstream Scorecard the primary interface for reading and explaining published results and for running diagnostics. Use the MCP for its supported queries and explanations, and the same installed binary's CLI for fresh selected scans and local file checks. Preserve the controller's useful evidence-handling capabilities until upstream can replace them without loss.

This is a selective replacement of controller-driven interaction, not a requirement to remove every script. It should give maintainers more capability while reducing duplicated integration logic. The first integration release uses a user-installed Scorecard executable; hosted MCP development proceeds independently and does not block it.

## Current implementation

- [.mcp.json](../../.mcp.json) starts only `bestpractices`, using `best-practices-mcp==0.7.0` through `uvx`.
- [The Scorecard skill](../../skills/ossf-scorecard/SKILL.md) uses [scripts/scorecard.py](../../scripts/scorecard.py) for `fetch`, `explain`, and `diff`. Its tool permissions reference that controller. It explicitly says the plugin does not install or orchestrate Scorecard binaries.
- The controller reads public API results without credentials, imports upstream JSON, saves original documents with acquisition provenance, and compares snapshots conservatively. It does not scan repositories.
- [Authentication and results guidance](../../skills/ossf-scorecard/references/authentication-and-results.md) treats CLI diagnostics as an already established user workflow. [Publication guidance](../../skills/ossf-scorecard/references/action-publication.md) distinguishes diagnostics from public results.
- [Controller tests](../../tests/test_scorecard.py), [documentation integrity tests](../../tests/test_documentation_integrity.py), [engineering evaluations](../../tests/engineering-skill-evals.md), README text, and CI checks encode aspects of this behavior.

## Upstream baseline and boundaries

Use v5.7.0 as the initial compatibility candidate, then validate the exact release selected for implementation. `scorecard mcp` ships inside the full Scorecard binary. The released MCP uses stdio and reads precomputed public results; it does not execute scans. Installing the binary locally makes the CLI available to an agent with shell access, but does not make CLI operations callable through MCP.

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
| Save an original published baseline | Retain controller `fetch --output` | MCP summaries cannot reconstruct all upstream evidence |
| Interpret supplied JSON | Retain controller `explain` initially | Preserves the import path and normalization already supported |
| Compare saved results | Retain controller `diff` | Neither current MCP nor supported public CLI replaces the provenance checks |
| Configure publication and verify badge update | Existing publication procedure | Fresh diagnostics do not publish to the public API |

Avoid duplicate routine acquisition: use MCP for conversational queries; use the controller when an original published snapshot is required. If both are used, compare target commit, measurement date, and scanner identity before treating them as the same measurement. The latest public result can change between calls.

## Proposed changes, in implementation order

### 1. Rehearse installation and define the supported configuration

Document user installation from upstream's supported release distribution. The plugin should declare a `scorecard` MCP entry equivalent to `command: scorecard` with `args: [mcp]`; preserve the existing Best Practices entry. Rehearse PATH discovery in an actual plugin host and document the supported absolute-path override mechanism before relying on it.

Record the tested Scorecard version and platforms. Distinguish a minimum supported version from an exact runtime pin: a PATH-resolved user binary is not pinned merely because documentation names a version. Choose a compatibility policy and report the observed version when diagnosing behavior. CI should use an exact tested release with artifact verification appropriate to upstream distribution.

Do not add committed binaries, automatic downloads, installer hooks, global PATH modification, or a custom MCP client in this pass. Do not reuse the Python `requirements-mcp.txt` pin mechanism for a Go executable. Confirm that a missing optional Scorecard executable does not prevent users from using the other skills; if the host handles this poorly, resolve the configuration strategy before release.

Acceptance: a clean setup connects; missing/old executables produce actionable instructions; ordinary published queries require no GitHub token; existing Best Practices behavior remains functional.

### 2. Update skill orchestration and permissions

Replace controller-first routine queries with MCP operations. Update the skill's entry paths, frontmatter permissions, and reference documents to reflect direct CLI diagnostics. Validate actual plugin-qualified MCP tool names and host permission syntax; do not guess them or grant broad shell access merely for convenience.

Keep the durable skill focused on when to use each interface, how to select the target repository/checks, and how to interpret evidence. Let upstream tool schemas describe parameters. Put installation, version troubleshooting, CLI examples, and evidence details in focused references rather than duplicating long descriptions in the skill.

If MCP is unavailable, diagnose the connection without silently installing software. Existing supplied-result analysis and snapshot commands can remain useful fallbacks. Lack of a published result should offer a fresh diagnostic when appropriate, not automatically install an Action or demand publication. Preserve GitLab record/import support without implying parity for every scan or publication workflow.

### 3. Add deliberate CLI diagnostic workflows

Teach two explicit paths: a targeted remote scan for fresh repository evidence, and local file preflight for checks supported by `--local`. Select relevant checks rather than running every check for a narrow question. Use the project's actual directory, quote paths, and select a new output path without overwriting the baseline. Save requested details and annotations; use debug verbosity when the investigation needs details filtered at the default level.

Record the command's scope, target, installed scanner build, result commit/date, credentials' relevant access limitations, and whether the result is local, remote diagnostic, or published. Record no secret values. Inspect exit status and result availability together: a scan may fail some checks while leaving useful evidence. Verify exact behavior against the selected release and preserve usable partial results with clear limitations.

Keep credentials in the user's environment or normal secret tooling. Cached public queries do not need a token; remote diagnostics may. Diagnose the specific permission gap before broadening access. For publication use the existing Action authentication procedure. Do not create or publish workflows just to make a diagnostic run possible.

Acceptance: the agent can run a fresh selected check and explain its JSON, perform a supported local preflight, and distinguish both from public badge verification. Do not add a Python execution wrapper unless a concrete orchestration need emerges that direct CLI use cannot reasonably satisfy.

### 4. Preserve evidence and reduce duplication conservatively

Keep `fetch --output`, `explain`, and `diff` initially. Review their user-facing descriptions so the controller is presented as an evidence utility rather than the only Scorecard interface. Do not remove tested functionality solely to reduce line count. Refactor or delete only after a replacement demonstrates parity and no retained caller needs it.

Preserve upstream annotations and unknown fields in original snapshots. Do not feed MCP summaries or controller interpretation output into a path expecting a saved original report. Distinguish check absence, inconclusive status, and interface truncation. An incomplete result is not necessarily unusable.

Keep comparison safeguards for repository identity, scanner version/commit, source, check coverage, inconclusive-state changes, and chronology. A fresh scan of a selected subset is not interchangeable with a full published scan; even two complete reports can differ in credentials or engine behavior. Explain why an aggregate delta is withheld while retaining useful per-check observations.

### 5. Revise remediation and planning guidance

Explicitly allow score-motivated incremental improvements. Replace the playbook's categorical preference against projected score lift with guidance that considers user goals, usefulness, effort, maintenance, and likely detector recognition together. A small real implementation can be worthwhile; it need not be a project's highest-priority security investment.

Use the Atheris case as a behavioral example: investigate how the relevant scanner version recognizes Python fuzzing, add a modest useful target, exercise it, preflight where supported, then verify a later remote result. Local and remote Fuzzing language selection differ, so a local success is not a guarantee of remote detection. The skill should permit ordinary upstream source inspection without maintaining its own detector implementation.

Distinguish implementation value, expected recognition, and observed score effect. Do not invent practices, reviews, contributors, or releases. Keep longitudinal work explicit: proposed, implementing, PR open, reviewed, merged, awaiting measurement, observed. A Markdown plan is sufficient when useful; no new persistence subsystem is required. History-dependent checks should lead to realistic follow-up work rather than promises of a large score increase in one session.

### 6. Document, evaluate, and prepare a release proposal

Update README installation and Scorecard sections, the three Scorecard references, skill permissions/instructions, contribution/test guidance where affected, and behavioral evaluations. Preserve the independent Best Practices workflow and terminology. Add an Unreleased changelog entry when implementation changes user behavior; select a release version through the normal release process, not in this planning commit.

Audit release packaging and validation so any added documentation/configuration is included intentionally. A successful manifest validator does not prove executable availability, connection behavior, or tool correctness. Keep those checks distinct. Do not tag, publish, push, or configure a hosted endpoint as part of implementing this plan unless separately requested.

## Validation plan

| Layer | Required evidence |
| --- | --- |
| Offline regression | Existing Scorecard parsing/snapshot/diff cases continue to pass; meaningful new cases cover any changed behavior |
| Evidence fidelity | Original documents retain annotations/unknown fields; capped MCP results never masquerade as complete snapshots |
| Comparison behavior | Mismatched engines, sources, check sets, inconclusive results, chronology, and same-commit measurements remain explicit |
| Documentation integrity | Command examples, references, permissions, and MCP configuration agree with actual interfaces |
| Upstream contract | Real selected Scorecard binary initializes and serves catalog/explanation tools; controlled REST responses exercise query/error/truncation paths |
| CLI integration | A small disposable fixture exercises a supported local check and JSON import without scanning or modifying a real project |
| Actual host | Fresh plugin installation, PATH discovery, missing binary, tool naming, coexistence with Best Practices, and connection restart |
| Behavioral evaluation | Published diagnosis, no published result, narrow fresh scan, local fuzzing preflight, supplied partial JSON, incompatible comparison, and post-merge verification |

Keep ordinary tests offline and retain subprocess coverage aggregation and both coverage floors. Separate tests needing the real Scorecard executable/network from `make test`. Add an appropriately named Make target using a configurable `SCORECARD` executable variable if repeated contract checks need one; do not make unrelated Best Practices contract tests depend on Scorecard. Use existing `venv` tooling for Python tests.

During implementation run focused checks and then `make check`, the relevant real-server contracts, and `make plugin-validate` when available. Record actual host/skill evaluations separately from unexecuted scenarios. CI changes must use SHA-pinned actions, minimal read-only top-level permissions, and job-scoped elevations only when needed. Resolve exact versions and SHAs at implementation time.

## Suggested commit boundaries

1. MCP configuration, supported-installation documentation, and connection/contract validation.
2. Skill MCP/CLI routing, permission changes, and relevant behavioral/documentation checks.
3. Evidence utility adjustments only where necessary, with regression coverage in the same commit as changed behavior.
4. Remediation and longitudinal planning guidance with recorded evaluations.
5. Release-facing documentation/changelog and any coordinated version change when ready.

Keep each commit coherent and passing; combine dependent documentation/tests with the behavior they verify. These boundaries are guidance, not a reason to leave stale instructions temporarily active.

## Hosted transition contract

The Scorecard fork owns HTTP transport, service deployment, and proposed export/comparison/live-scan tools. Badge Buddy owns installation guidance, skill orchestration, and user workflows. The local integration must not wait for the hosted track.

A hosted binary does not give the client shell access to the CLI. Only exposed server tools become remotely available. Keep local diagnostics as an optional enhancement when a hosted endpoint arrives. Do not promise local workspace inspection over HTTP or silently upload source. Introduce an experimental channel only when it helps real testing; avoid a permanent duplicate skill codebase.

When upstream or the fork offers complete exports/comparisons, reassess the retained controller through the same parity tests. Transport changes alone are not grounds to remove it. Coordinate live scanning with [upstream issue #5413](https://github.com/ossf/scorecard/issues/5413); HTTP is also on the [MCP roadmap](https://github.com/ossf/scorecard/blob/v5.7.0/docs/mcp.md#roadmap).

## Decisions to resolve during implementation

- Exact supported release/platform matrix and how incompatibility is detected without a custom launcher.
- Host-supported absolute-path override and behavior when Scorecard is absent, including impact on other skills.
- Exact MCP tool permission declarations and the narrowest practical CLI permission policy.
- Which live contract and CLI checks belong in CI, how verified binaries are obtained there, and how failures are reported independently of Best Practices.
- Whether any controller simplification is justified after MCP adoption; default to retaining evidence capabilities.
- Which behavioral scenarios have been run successfully enough to support the first integration release.

No hosting provider, public endpoint, install automation, or release date is selected by this plan.

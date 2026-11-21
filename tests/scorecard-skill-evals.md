# Scorecard integration evaluations

These scenarios check agent decisions separately from offline documentation checks and `make test-scorecard` contracts. A specification is not evidence that a model followed it. Record actual tool calls, results, model/client versions, prompts, plugin content hashes, and limitations. The full Passing-application benchmark is a separate planned project; these are focused integration rehearsals.

Use a disposable workspace and plugin copy, controlled public-result responses, and isolated MCP configuration. Keep repository credentials, real application state, publication, and unrelated tools out of the session. Model-provider authentication can remain with the host. Explicit skill invocation checks the procedure; it does not establish automatic activation. Use repeated trials and a plugin-disabled comparison when measuring reliability rather than rehearsing a change.

## Behavioral scenarios

| Scenario | Expected observations |
| --- | --- |
| Current published status | Start with an MCP overview scoped to the question. Report the target repository commit/date separately from the scanner build commit and installed executable. Do not routinely request all details or write reports. |
| Selected-check investigation | Request relevant check details; inspect `details_total` and `details_truncated`, increasing `max_details` within the supported 500-entry cap when useful. A detail count is not a defect count. Investigate detector recognition without requiring an unrelated effectiveness assessment. |
| Missing binary/server | Diagnose installation, selected path, version, or connection. Do not substitute a scripted query backend or require Scorecard for another skill. |
| No published result | A missing result is not zero. Offer a scoped fresh diagnostic when helpful; do not install publication automatically. |
| Fresh selected remote diagnostic | Use the same executable as MCP, select relevant checks, a fresh output path, and environment credentials. Record scanner identity, scope, mode, access limits, exit status, and usable output. No claim that the result was published. |
| Local fuzzing preflight | Inspect supported local evidence with the selected executable. Allow useful score-motivated improvements, investigate detector recognition, and distinguish local language selection from remote prominence. |
| Nonzero exit with fresh valid partial JSON | Preserve useful check results and the failure status; identify inconclusive checks and keep the result separate from successful complete measurement. |
| Failed scan with absent or malformed output | Report a failed measurement; do not reuse an older file, invent a new score, or discard an existing baseline. |
| Commit-specific historical comparison | Query `get_repo_score` with each target repository commit SHA, then relevant `get_check_result` calls at those same commits. Use existing metadata and link the measurements; no GitHub access, full-report export, or saved baseline is inherently required. |
| Workflow-report comparison | When MCP evidence is unavailable or insufficient, inspect an existing uploaded JSON report through ordinary host tools, or logs containing useful results. Check repository/commit/date and actual coverage; logs may omit or truncate results. Do not require a new workflow, client, credential store, or archive. |
| Supplied partial JSON | Inspect supplied documents with ordinary host tools, including without an installed Scorecard binary. Explain missing fields and retain useful per-check evidence; do not require import conversion or a provenance sidecar. |
| Differing scanner/check coverage | Compare actual check sets and conclusive scores, source, scanner build, scope, access, and chronology. `complete` is relative to expected check names in the running server catalog, not the historical catalog, conclusive scores, or untruncated detail. Do not recompute an aggregate or imply comparable aggregates when conditions differ. |
| Inconclusive becomes conclusive | Explain `-1` to a numerical score as newly conclusive evidence, not a numerical gain from `-1`; absent and zero remain distinct. An incomplete result can support comparisons of checks present in both results. |
| Unavailable historical evidence | State when commit-specific records, retained artifacts, or useful logs are unavailable. Use what exists without inventing a baseline or requiring one to have been saved earlier. |
| Optional saving | Ordinary queries and comparisons make no automatic report writes. When the user requests JSON at a chosen destination, save available upstream JSON using ordinary host tools and permissions; do not label a projected summary as a lossless raw report or create a plugin storage format. |
| GitLab subgroup | Explain the tested MCP limitation and investigate available evidence only within the user’s scope. No controller workaround, equivalent platform coverage promise, or automatic GitHub publication workflow. |
| Post-merge verification | A green publishing job is insufficient when the public record still names an older commit. Report publication pending and distinguish observed score changes from causal claims and expectations. |

Execution transcripts and development-run reports are not distributed with the plugin. The scenarios above describe intended evaluation coverage; they are not independent evidence of model reliability.

## Attended release smoke tests

Run these against the final installed candidate and record results privately. Passing deterministic contracts or reviewing this matrix does not establish host or agent behavior.

- Fresh plugin installation, PATH discovery and absolute-path override, MCP tool naming, same-executable CLI selection, and restart after changing the launch environment.
- Missing executable, failed connection, intentional MCP/CLI executable mismatch, and continued independent Best Practices use.
- Current status and selected-detail investigation, historical MCP comparison, workflow-report alternatives, supplied JSON, unavailable baseline, and an optional requested save as specified above.
- Fresh targeted diagnostic and local preflight, useful partial output, failed output, and post-merge publication verification in an authorized disposable context.

Review application/reviewer and cross-skill behavior separately when accepting the whole release. These are outstanding smoke-test requirements until actual execution evidence for the candidate establishes otherwise; this document records no model reliability results.

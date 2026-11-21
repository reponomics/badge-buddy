# Scorecard integration evaluations

These scenarios check agent decisions separately from the controller's offline unit tests and `make test-scorecard` contracts. A specification is not evidence that a model followed it. Record actual tool calls, results, model/client versions, prompts, plugin content hashes, and limitations. The full Passing-application benchmark is a separate planned project; these are focused integration rehearsals.

Use a disposable workspace and plugin copy, controlled public-result responses, and isolated MCP configuration. Keep repository credentials, real application state, publication, and unrelated tools out of the session. Model-provider authentication can remain with the host. Explicit skill invocation checks the procedure; it does not establish automatic activation. Use repeated trials and a plugin-disabled comparison when measuring reliability rather than rehearsing a change.

## Behavioral scenarios

| Scenario | Expected observations |
| --- | --- |
| Published diagnosis | Ordinary repository and selected-check queries use MCP. Explain zero, inconclusive, absent, and truncated evidence distinctly. Report the historical measurement identity separately from the installed engine. |
| Missing binary/server | Diagnose installation, selected path, version, or connection. Do not invoke controller capture as a query fallback or require Scorecard for another skill. |
| No published result | A missing result is not zero. Offer a scoped fresh diagnostic when helpful; do not install publication automatically. |
| Fresh selected remote diagnostic | Use the same executable as MCP, select relevant checks, a fresh output path, and environment credentials. Record scanner identity, scope, mode, access limits, exit status, and usable output. No claim that the result was published. |
| Local fuzzing preflight | Inspect supported local evidence with the selected executable. Allow useful score-motivated improvements, investigate detector recognition, and distinguish local language selection from remote prominence. |
| Nonzero exit with fresh valid partial JSON | Preserve useful check results and the failure status; identify inconclusive checks and keep the result separate from successful complete measurement. |
| Failed scan with absent or malformed output | Report a failed measurement; do not reuse an older file, invent a new score, or discard an existing baseline. |
| Supplied partial reports and incompatible comparison | Inspect files offline. Keep per-check evidence but withhold unsupported aggregate deltas; engine/source/scope/access limitations remain explicit. |
| GitLab subgroup | Explain the tested MCP limitation, capture to an explicit path, then inspect that original file. Do not turn it into a general query fallback or a GitHub publication workflow. |
| Post-merge verification | A green publishing job is insufficient when the public record still names an older commit. Report publication pending and distinguish measured effects from expectations. |

Execution transcripts and development-run reports are not distributed with the plugin. The scenarios above describe intended evaluation coverage; they are not independent evidence of model reliability.

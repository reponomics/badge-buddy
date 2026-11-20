# Results, credentials, and CLI diagnostics

## Read published evidence through MCP

Use the upstream MCP for ordinary published overviews and selected-check findings. It reads existing REST records without credentials and does not start a scan. Its overview omits detailed findings, its single-check output can be truncated, and its provider selects fields from the original response. Do not reconstruct a supposedly lossless snapshot from these summaries. Missing checks, inconclusive scores, and truncation describe different limitations.

Explain the supplied score without recalculating an aggregate. Details, documentation, or an overall score may be absent. Inspect reported file locations at the measured revision and check upstream documentation for that engine version. The installed MCP's explanation catalog describes its own build, which need not match an older result. Maintainer annotations are context, not proof that a finding was resolved.

## Save and inspect original evidence

Resolve [the evidence controller](../../../scripts/scorecard.py) relative to this reference, then use its absolute path for `<scorecard-controller>` below. Replace the other placeholders and quote shell paths. It uses the Python standard library, reads supplied documents, and captures public records; it neither scans nor publishes.

For an explicit original baseline, capture the upstream API document:

```bash
"<scorecard-controller>" fetch --repo <owner/repo> --output <new-baseline-path>
```

`--output` is required. The response confirms the saved path and measurement/provenance identity; findings remain in the saved document. The snapshot preserves the original fields, including annotations and unknown fields, with acquisition provenance added. Preserve the baseline and use a new path for the next measurement, outside the repository unless requested otherwise. This is an evidence operation, not a backup for an unavailable MCP connection.

Upstream v5.7.0 MCP does not accept GitLab subgroup paths. For that specific limitation, capture the original published record with `--repo gitlab.com/group/subgroup/project --output <path>`, then inspect the saved JSON. Do not assume GitHub Action publication applies to GitLab.

Inspect supplied API snapshots or conventional upstream CLI JSON offline:

```bash
"<scorecard-controller>" explain --input <path>
```

Use `--input -` for stdin. Imported documents can lack provenance, version, details, or a usable commit. Keep those limits explicit. The controller accepts Scorecard JSON, not SARIF; inspect SARIF in the relevant code-scanning tooling or obtain a JSON report from the Action artifact.

Compare original report files, never MCP summaries or controller interpretation output:

```bash
"<scorecard-controller>" diff --before <baseline-path> --after <new-result-path>
```

The controller retains useful per-check observations but withholds an aggregate delta when available evidence is incompatible. Read notes about repository, source, engine, check coverage, chronology, and inconclusive results. Even a permitted delta establishes structural comparability, not equal credentials or invocation conditions. A selected-check diagnostic and a full published run are different measurements. If scope/access context is unknown, say so.

## Acquisition failures

A missing public record has no score to interpret. Offer a fresh targeted diagnostic when it answers the question; discuss publication only when useful to the user's request. Correct invalid repository input before retrying. For rate limits, service failure, or network problems, report the cause and retry with bounded pacing. Do not change workflows or request a token for the unauthenticated public API. An unavailable MCP connection requires [connection diagnosis](installation.md), not a fallback query through the controller.

## Action credentials

Prefer the workflow's built-in `GITHUB_TOKEN`. Check [current Action authentication guidance](https://github.com/ossf/scorecard-action#authentication-with-fine-grained-pat-optional) when a specific finding lacks access. Classic branch-protection visibility can require additional credentials; repository rulesets can be read with the default token. Investigate the actual failure before broadening access.

If optional credentials are selected, follow the [upstream fine-grained token procedure](https://github.com/ossf/scorecard-action/blob/main/docs/authentication/fine-grained-auth-token.md), limiting access to the required repository and operation. Have the user supply secrets through their environment or repository secret manager, never in chat or committed files. Confirm any organization approval and expiration requirements. Read [action-publication.md](action-publication.md) before changing publication permissions or verifying publication.

Before adopting an optional token, explain its upkeep and carry the accepted responsibility into the handoff: who will renew or replace it, its actual expiry or replacement trigger, and which named secret they must update. Explain which checks or workflow depend on it and may lose access or fail when it expires. Verify the next run after replacement. Do not invent a rotation schedule or assign manual renewal work for the built-in `GITHUB_TOKEN`.

## CLI diagnostics

The CLI is a supported execution path through the same required binary as the MCP. Before its first use, follow [installation and executable selection](installation.md). Resolve `<scorecard-executable>` to that selected absolute path, including any override used by the host. Use the current upstream [CLI guidance](https://github.com/ossf/scorecard/tree/v5.7.0#scorecard-command-line-interface) and that build's `--help` when a flag or platform is uncertain.

Select checks for the question. A targeted remote diagnostic might be:

```bash
diagnostic_dir=$(mktemp -d) || exit 1
"<scorecard-executable>" --repo=github.com/OWNER/REPO --checks=Pinned-Dependencies --show-details --show-annotations --format=json --output "$diagnostic_dir/remote.json"
scan_status=$?
printf 'Scorecard exit status: %s\nReport path: %s\n' "$scan_status" "$diagnostic_dir/remote.json"
```

A supported local file preflight might be:

```bash
diagnostic_dir=$(mktemp -d) || exit 1
"<scorecard-executable>" --local="/absolute/path/to/project" --checks=Fuzzing --show-details --show-annotations --format=json --output "$diagnostic_dir/local.json"
scan_status=$?
printf 'Scorecard exit status: %s\nReport path: %s\n' "$scan_status" "$diagnostic_dir/local.json"
```

Replace the repository, project path, and checks for the task. Run each example in one shell invocation so the captured exit status and path are printed before temporary shell variables disappear. These illustrate separate runs; inspect the first before starting another. A newly created directory prevents a stale report from masquerading as fresh output. Save stderr and the printed exit status when diagnosing a failure. Do not chain output inspection behind `&&`, since a failed scan can still emit useful JSON. Add `--verbosity=debug` when the investigation needs findings filtered at the default detail level.

After each run, inspect the exit status and the newly produced file together. A nonzero exit with valid JSON can supply partial findings: preserve them, identify failed/inconclusive checks, and report the run as incomplete. A nonzero exit with absent or malformed output is a failed measurement, not a new score. A zero exit also needs inspection for skipped/absent checks and inconclusive evidence. Use `explain --input` only after validating the report is newly produced and usable.

For remote repositories, v5.7.0 requires suitable credentials in the environment: use upstream-supported GitHub or GitLab token configuration and diagnose the specific access gap. Keep secrets out of chat, command arguments, saved reports, and committed files. The local mode does not require a repository token, but local analysis can still use external data; it is not a general offline guarantee. Do not create a publishing workflow just to run a diagnostic.

Record the output path, exact nonsecret command, selected executable version/build, target/check scope, mode (local or remote diagnostic), result commit/date, and relevant credential access limitations in the handoff or an existing work log. Do not create a new storage subsystem. Bare CLI reports enter the controller as generic imports; they do not capture every invocation condition.

Local mode runs supported file checks and skips host settings/history checks. It can inspect uncommitted files; its result is not remote verification. Fuzzing's local language selection differs from remote language prominence, so a detected local target does not promise remote recognition. A fresh remote CLI scan does not publish to the public API. Verify public badge changes through a later published record as described in [action-publication.md](action-publication.md).

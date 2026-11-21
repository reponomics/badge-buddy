# Find results and run diagnostics

## Find earlier measurements

For historical comparison, first retrieve the published overview at each target repository commit SHA through MCP, then relevant check details at those same commits. If those records are unavailable or insufficient, inspect the repository's existing workflow runs. Use the same run commands when investigating a failed scan or checking publication.

### Retrieve a workflow run and its logs

For GitHub, use the host's connected tools or an authenticated GitHub CLI. Choose the Scorecard workflow filename from `.github/workflows/`, then list its runs. Replace `OWNER/REPO`, `WORKFLOW_FILE`, and the IDs below with actual values:

```bash
gh run list --repo OWNER/REPO --workflow WORKFLOW_FILE --limit 20
```

Add `--commit TARGET_SHA` for a particular revision or `--created YYYY-MM-DD` to narrow the search. Inspect the selected run and its logs:

```bash
gh run view RUN_ID --repo OWNER/REPO
gh run view RUN_ID --repo OWNER/REPO --log
```

For a large run, use a job ID from the summary to retrieve only that job's log:

```bash
gh run view RUN_ID --repo OWNER/REPO --job JOB_ID --log
```

If the summary lists an uploaded report, prefer that artifact for structured comparison. Retrieve only the selected artifact into a temporary directory:

```bash
report_dir=$(mktemp -d) || exit 1
gh run download RUN_ID --repo OWNER/REPO --name ARTIFACT_NAME --dir "$report_dir"
```

Check the report's measured revision and date against the run metadata; the report establishes what was measured. Logs may omit or truncate results, and logs and artifacts are subject to retention. If useful older evidence is unavailable, say so and use what exists. Read existing reports with ordinary host tools.

Command reference: [list runs](https://cli.github.com/manual/gh_run_list), [view runs and logs](https://cli.github.com/manual/gh_run_view), and [download artifacts](https://cli.github.com/manual/gh_run_download).

## Compare measurements

Identify each measurement's repository, target commit, date, scanner version/build, and source; link the measurements or workflow runs used. The target repository commit identifies measured code, while `scorecard.commit` identifies the scanner build. State any missing context in supplied reports.

Compare actual check sets and conclusive coverage. `missing_checks` uses the running MCP server's catalog of expected non-experimental checks for the platform, not the historical scanner's catalog. `complete: true` means those names are present, not that every score is conclusive or every detail is returned. An incomplete result can still support comparison of checks present in both measurements.

Missing, inconclusive (`-1`), and zero are distinct. A transition from `-1` to a numerical score is newly conclusive evidence. Explain per-check changes and reported aggregates where comparable, without recomputing an aggregate. Differences in scanner build, source, check scope, chronology, credentials, or invocation conditions limit comparison. Even measurements of the same commit can differ as settings or external data change; an observed score change alone does not establish its cause.

## Unavailable results

A not-found response means the API lacks the requested repository/commit record; an existing workflow report may still be available. For invalid input, correct the request. For rate limits or service failures, retry with bounded pacing. For a failed MCP connection, follow [installation troubleshooting](installation.md#check-the-connection). Published API queries require no GitHub token.

Upstream v5.7.0 MCP rejects GitLab subgroup paths. Explain that limitation and inspect available evidence within the user's scope. Consult upstream platform support before proposing diagnostics or publication; the GitHub Action procedure applies to GitHub repositories.

## Action credentials

Prefer the workflow's built-in `GITHUB_TOKEN`. If a specific check lacks access, consult [upstream authentication guidance](https://github.com/ossf/scorecard-action#authentication-with-fine-grained-pat-optional) before broadening permissions. Classic branch-protection visibility can require additional credentials; repository rulesets can be read with the default token.

For an optional token, follow the [fine-grained token procedure](https://github.com/ossf/scorecard-action/blob/main/docs/authentication/fine-grained-auth-token.md), restrict access to the required repository and operation, and use the repository secret manager. Confirm organization approval, expiry, who will replace the token, and which secret and checks depend on it. Verify the next run after replacement. The built-in token needs no manual renewal plan.

## CLI diagnostics

Run a fresh diagnostic when the user requests one or when current findings are needed to validate selected work. This requires the [installed executable selected for MCP](installation.md#select-one-executable-for-both-interfaces). Replace `<scorecard-executable>` below with its absolute path; consult its `--help` and [upstream CLI guidance](https://github.com/ossf/scorecard/tree/v5.7.0#scorecard-command-line-interface) for supported flags and platforms.

Select checks for the question. A targeted remote diagnostic might be:

```bash
diagnostic_dir=$(mktemp -d) || exit 1
scan_status=0
"<scorecard-executable>" --repo=github.com/OWNER/REPO --checks=Pinned-Dependencies --show-details --show-annotations --format=json --output "$diagnostic_dir/remote.json" || scan_status=$?
printf 'Scorecard exit status: %s\nReport path: %s\n' "$scan_status" "$diagnostic_dir/remote.json"
```

A supported local file preflight might be:

```bash
diagnostic_dir=$(mktemp -d) || exit 1
scan_status=0
"<scorecard-executable>" --local="/absolute/path/to/project" --checks=Fuzzing --show-details --show-annotations --format=json --output "$diagnostic_dir/local.json" || scan_status=$?
printf 'Scorecard exit status: %s\nReport path: %s\n' "$scan_status" "$diagnostic_dir/local.json"
```

Replace the repository, project path, and checks for the task, and run each example in one shell invocation. Each new directory prevents reuse of stale output; the failure clause captures the exit status even under `set -e`. Inspect that status, stderr, and the new report together. A failed scan can still provide useful partial findings. Missing or malformed output is a failed measurement, and a zero exit still needs inspection for absent or inconclusive checks. Add `--verbosity=debug` when needed to include findings filtered at the default detail level.

For remote GitHub or GitLab diagnostics, configure [upstream-supported authentication](https://github.com/ossf/scorecard/tree/v5.7.0#authentication): token environment variables or GitHub App configuration where applicable. Diagnose access errors from the actual command and check output. Supply secrets through the environment or secret manager, never in chat or committed files. Local mode does not require a repository token, though some checks use external data.

When explaining the result, include the nonsecret command, executable build, target/check scope, local or remote mode, and relevant access limits. These conditions matter when [comparing measurements](#compare-measurements).

Local mode selects checks marked as supporting file-based requests. Default selection filters out unsupported checks; explicitly naming one with `--checks` returns an error under the [v5.7.0 selection policy](https://github.com/ossf/scorecard/blob/v5.7.0/policy/policy.go). It can inspect uncommitted files; its result is not remote verification. A fresh remote CLI scan does not publish to the public API. Verify public badge changes through a later published record as described in [action-publication.md](action-publication.md).

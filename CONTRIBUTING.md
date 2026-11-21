# Contributing to Badge Buddy

Thank you for helping. This page covers the development setup, the coding standard, the test policy, and how changes are versioned.

## Set up and check your work

You need Python 3.11 or newer and `make`. The live tests also need [uv](https://docs.astral.sh/uv/getting-started/installation/), and plugin validation needs the Claude Code CLI.

```bash
make setup
```

```bash
make check
```

`make check` verifies formatting and lint rules, runs the tests offline with the coverage floor, and compiles the Python sources. These additional checks run in CI and can be run locally:

| Command | What it does |
| --- | --- |
| `make test-live` | Starts the pinned MCP package with `uvx`; checks documented tools and all board levels, then exercises draft and proposal contracts with synthetic HTTP responses and isolated storage |
| `make test-scorecard` | Starts the separately installed, tested Scorecard executable; checks MCP tools against controlled REST responses and CLI scans against disposable local repositories. Set `SCORECARD=/absolute/path/to/scorecard` to select it |
| `make plugin-validate` | Runs `claude plugin validate --strict` on the plugin and marketplace manifests |
| `make check-board-browser` | Generates an offline mixed-answer fixture and checks navigation, responsive layout, refresh, revisions, and safe rendering in headless Chromium |

For browser checks, use Node.js 24 and npm. Run `make setup-board-browser` once to install the pinned CI dependencies and download Chromium. On Linux, `make setup-board-browser PLAYWRIGHT_INSTALL_ARGS=--with-deps` can also install Chromium's system dependencies. Subsequent browser checks need no existing tab, MCP server, or external service; the runner creates and cleans up its own temporary files and loopback HTTP server.

To try your working copy in Claude Code, start it with `claude --plugin-dir .`.

## Coding standard

Python code follows [PEP 8](https://peps.python.org/pep-0008/) as applied by the [Ruff formatter](https://docs.astral.sh/ruff/formatter/), together with the lint rules selected in [ruff.toml](ruff.toml). CI enforces both. `make format` applies the formatter and the safe lint fixes.

An exception to a lint rule is made on the line it applies to, with `# noqa: <rule>` and a comment that gives the reason.

Documentation is written in plain prose without hard wrapping.

## Tests

Tests for new functionality must be added to the automated test suite in the same pull request as the functionality. A bug fix comes with a regression test that fails without the fix.

The suite must keep at least 80% statement coverage and 80% branch coverage of `scripts/` and `tools/`; `make check` enforces each floor separately using the unrounded counts in `coverage/coverage.json`. The combined percentage in the text report is informational. Each run erases old measurements, collects Python subprocess execution with coverage.py's subprocess patch, and combines the resulting data before reporting. This includes the board command exercised by CLI tests. Tests run offline: they use a stand-in MCP server and make no network requests. Checks that need the real server belong in `tests/live/`.

Skill and reference documents are instructions for Claude, so unit tests alone cannot establish their behavior. When you change them, say in the pull request how you tried the change. The [badge workflow evaluations](tests/badge-skill-evals.md), [Scorecard evaluations](tests/scorecard-skill-evals.md), and [engineering skill evaluations](tests/engineering-skill-evals.md) describe behavioral scenarios, not published benchmark results. Keep execution transcripts and development-run reports in ignored local storage; publication requires a separate maintainer review of privacy, methodology, and claims. The Best Practices live contract suite uses the real pinned MCP package with controlled project responses; it does not write to BadgeApp or use your stored drafts. The independent Scorecard suite uses a real executable and controlled data; ordinary offline tests do not need that binary.

## Versions and the changelog

The plugin uses [Semantic Versioning](https://semver.org/). Users receive a new copy of the plugin only when the version in [.claude-plugin/plugin.json](.claude-plugin/plugin.json) changes, so a change that affects what the plugin does for a user is released under a new version. This includes changes to skill and reference instructions that alter the assistant's behavior. Explanatory documentation, tests, and CI changes that do not affect user-facing behavior need no version change. Group unreleased changes under the next release version; follow the release procedure when publishing them.

Describe each user-visible change under `Unreleased` in [CHANGELOG.md](CHANGELOG.md), written for someone deciding whether to upgrade.

### Changing the Best Practices MCP server version

The server version is pinned in two places that must agree: [.mcp.json](.mcp.json), which starts it, and [requirements-mcp.txt](requirements-mcp.txt), which dependency alerts and scans read. A pull request that changes the pin must also change the plugin version; CI checks both rules. Before raising the pin, read the server's [changelog](https://github.com/reponomics/best-practices-mcp/blob/main/CHANGELOG.md) and review the skill's tool list and the [application guide](skills/ossf-bp-badges/references/application.md) against it, then run `make test-live`.

### Changing Scorecard integration or compatibility

Scorecard is a user-installed Go executable, not a Python package in `requirements-mcp.txt`. The `pin-bump` CI guard above does not cover its compatibility policy or the skill's routing. A user-visible Scorecard change must explicitly include a plugin version bump and Unreleased changelog entry, including any new installation requirement or changed helper command. Review the selected upstream release, update the verified CI artifact and setup guidance together, run `make test-scorecard`, and record host and behavioral checks separately from tool-contract results. Follow the [release acceptance checklist](docs/release/releasing.md#scorecard-integration-acceptance) before tagging.

## Pull requests

Use a [Conventional Commits](https://www.conventionalcommits.org/) title, such as `fix: accept display identifiers in the board`. Keep a pull request to one purpose, and make sure `make check` passes. CI checks the title and the three acknowledgments in the pull request template.

Contributions must comply with the [Developer Certificate of Origin](docs/DCO.txt). Use `git commit --signoff` to record your certification with a `Signed-off-by` trailer. A trailer is not mandatory on every commit; do not ask an agent to certify changes on your behalf before you have reviewed or approved them. DCO signoff and cryptographic commit signing are separate.

Participation follows the [code of conduct](CODE_OF_CONDUCT.md), and suspected vulnerabilities are reported as described in [SECURITY.md](SECURITY.md).

Maintainers cut releases as described in [Releasing](docs/release/releasing.md).

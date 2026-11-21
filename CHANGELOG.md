# Changelog

Notable changes to Badge Buddy, newest first. Versions follow [Semantic Versioning](https://semver.org/). Standalone releases use signed tags; see [verifying a release](docs/release/verification.md).

## [Unreleased]

Planned plugin version: `0.5.0-beta.1`.

### Added

- Upstream Scorecard MCP for published results and check explanations, plus direct CLI workflows for fresh targeted scans and supported local checks. Both use the same user-installed executable; v5.7.0 is the tested compatibility baseline.
- Scorecard connection and executable troubleshooting, evidence-preserving diagnostic guidance, and a separate real-binary contract suite with controlled API responses and disposable local repositories.

### Changed

- Best Practices tool use follows the user’s stated goals and scope; draft synchronization is reserved for beginning or resuming draft work.
- Scorecard guidance supports useful incremental improvements motivated by the user's score goals, investigates whether the measured scanner recognizes them, and distinguishes local validation, fresh scans, publication, and progress that depends on project history.

### Breaking changes

- The integrated Scorecard workflow now requires a locally installed Scorecard executable with its MCP subcommand. The plugin does not install it. Best Practices and the other engineering skills remain independently usable. Supplied Scorecard reports can still be inspected offline.
- The Scorecard helper's `fetch` command now requires `--output` and returns capture confirmation and measurement provenance instead of the full interpreted result. Use MCP for ordinary published-result queries, or `explain --input` to inspect a saved original report. Snapshot comparison and GitLab subgroup capture/import remain available.

## [0.4.0-beta.1] - 2026-11-19

Badge Buddy now lives in its own repository and is its own plugin marketplace. Versions up to 0.3.0-beta.1 were published from the `reponomics/plugins` marketplace.

### Added

- A signed-tag release workflow and independent verification instructions. Standalone release tags use Claude Code's `badge-buddy--v<version>` convention; the workflow checks the authorized signer, manifest version, changelog, and release commit before publishing.

### Changed

- The OpenSSF Best Practices skill works through the [Best Practices MCP](https://github.com/reponomics/best-practices-mcp) server, which the plugin starts with `uvx`. The server finds your project's entry, reads saved answers and progress, keeps your draft, checks answers against each criterion's field rules, and builds the proposal URL you review in the browser. Installing [uv](https://docs.astral.sh/uv/getting-started/installation/) is now a prerequisite.
- Your draft is stored by the MCP server, one file per project, outside the plugin's data directory. At the start of a session the skill adds answers saved on the badge website that the draft lacks; it never overwrites an answer in your draft.
- A proposal URL carries only the answers that differ from the website.
- The preview board reads criterion text from the MCP server. Passing, Silver, and Gold criteria are grouped by the form's sections.
- Install with `claude plugin marketplace add reponomics/badge-buddy` and `claude plugin install badge-buddy@badge-buddy`.

### Removed

- The bundled command-line controller for the badge website, including its synchronization registry and the browser console fill script. Edits that a proposal URL cannot make, such as resetting an answer to unknown, are made in the form directly.
- The bundled criteria catalog. Criteria come from the MCP server.

### Fixed

- Preview justifications containing literal template markers now display correctly instead of breaking the board.
- On macOS and Linux, preview timeouts and failures stop both the MCP launcher and its server child, preventing a stalled child from keeping the renderer blocked.
- The badge skill and its peer reviewer explicitly treat instructions embedded in project evidence or criterion resources as untrusted content.
- Test coverage includes Python subprocesses used by the board renderer. Offline browser regressions and isolated tests against the pinned MCP server cover the installation's supporting components.

### Breaking changes

- Local drafts from earlier plugin versions are not automatically carried over to Best Practices MCP storage. Answers already saved to BadgeApp are retrieved when you resume work on a section. Previous draft files are left untouched.

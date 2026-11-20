# Install and connect Scorecard

The integrated Scorecard workflow requires the full upstream `scorecard` executable. That binary supplies both the read-only MCP server for published results and the CLI for fresh diagnostics. Other Badge Buddy skills do not require Scorecard. Conceptual discussion and inspection of already supplied JSON can proceed without it; they are not an alternate query backend.

## Compatibility and installation

Badge Buddy's first tested compatibility baseline is Scorecard **v5.7.0**, including `scorecard mcp`. Older builds are unsupported; newer builds need contract validation before being described as tested. The user's executable is not pinned by this plugin. CI tests an exact release, and the [recorded evaluations](../../../tests/scorecard-skill-evals.md) identify exercised hosts and platforms.

Use the upstream [installation instructions at v5.7.0](https://github.com/ossf/scorecard/tree/v5.7.0#installation) or its [release assets](https://github.com/ossf/scorecard/releases/tag/v5.7.0). On macOS, upstream documents Homebrew installation with `brew install scorecard`. Choose the build for the actual platform and follow upstream verification guidance when downloading a release. Installation or an upgrade is an explicit setup action; the plugin neither downloads a binary nor changes global PATH.

Check the selected executable before connecting:

```bash
command -v scorecard
scorecard version
scorecard mcp --help
```

Record the version, build commit, platform, and resolved executable path. An old executable without the MCP subcommand needs an upgrade; a service/network failure after connection is a different problem.

## Select one executable for both interfaces

The bundled `.mcp.json` uses `${BADGE_BUDDY_SCORECARD_BIN:-scorecard}` as its command and `mcp` as its argument. By default, the host resolves `scorecard` through its own PATH. A GUI host and an interactive shell can have different PATH values. For a stable explicit choice, set the override to an absolute executable path before starting Claude Code:

```bash
export BADGE_BUDDY_SCORECARD_BIN="/absolute/path/to/scorecard"
"$BADGE_BUDDY_SCORECARD_BIN" version
claude
```

Use that same absolute path for CLI diagnostics. Do not substitute whichever `scorecard` happens to appear first in a later shell. Resolve symlinks when comparing paths, and compare the executable's build with the configured server command, not with the engine version in an older published result. If the shell and MCP configuration select different binaries, stop the diagnostic, choose one, and reconnect before comparing results.

Claude Code supports [environment expansion in MCP commands](https://code.claude.com/docs/en/mcp#environment-variable-expansion-in-mcp-json). The variable must be present in the host's environment when it starts. An empty value does not select the default: unset it to use PATH. In a GUI, configure the environment through that host's supported launch mechanism and restart it; changing a shell after the GUI has started does not change its environment. Do not edit the cached plugin, add a duplicate server, or assume shell startup files configure the GUI.

## Check the connection

In Claude Code, `/mcp` should show `plugin:badge-buddy:scorecard`. Confirm its configured command is the executable selected above and exercise `list_checks`; a successful manifest validation does not prove the server started. The [plugin component documentation](https://code.claude.com/docs/en/plugins/components#server-names-tool-names-and-reloads) describes server naming and reconnection. After changing the launch environment, start a new host session; a plugin reload can keep an unchanged server connection.

The tool names are `mcp__plugin_badge-buddy_scorecard__` followed by the upstream tool name. The skill preapproves the five named read-only MCP operations and the bundled evidence controller. It leaves direct CLI execution under the user's normal shell permissions; it does not grant a wildcard for arbitrary executable paths. Claude Code's [MCP permission rules](https://code.claude.com/docs/en/permissions#mcp) use these full names.

When Scorecard is missing or fails to start, report the selected command and useful failure message, then diagnose installation, version, PATH, or connection state. Never replace a failed ordinary MCP query with the snapshot controller. Best Practices retains its separate server and workflow; do not request a Scorecard installation to perform unrelated badge, coverage, analysis, or workflow-maintenance work.

Inspect the actual host entry and launch environment before asserting a configuration mistake. Claude Code 2.1.327 can report `posix_spawn 'stdio'` for a nonexistent executable even when the configured command is a different absolute path; that label alone does not show that the command or override was set to `stdio`. If the effective command is unavailable, state that uncertainty rather than inventing its value. Likewise, `claude mcp list` can exit zero while an individual server reports failure; check the server status itself.

The upstream [MCP documentation](https://github.com/ossf/scorecard/blob/v5.7.0/docs/mcp.md) describes stdio operation. Its REST backend override changes where published records are read; it does not expose an HTTP MCP endpoint or enable live scans. No token is needed for the normal published-result queries.

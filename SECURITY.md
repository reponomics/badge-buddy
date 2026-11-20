# Security reporting

Report suspected vulnerabilities through [GitHub private vulnerability reporting for reponomics/badge-buddy](https://github.com/reponomics/badge-buddy/security/advisories/new). Do not post sensitive vulnerability details in public issues.

If you are unable to access this preferred reporting channel for some reason, you may also contact [security@reponomics.org](mailto:security@reponomics.org).

Include the affected version, your Claude Code version, the skill or script involved, the impact, and a minimal reproduction. Remove credentials and unrelated private data from examples. Use [public issues](https://github.com/reponomics/badge-buddy/issues) for ordinary bugs and [conduct@reponomics.org](mailto:conduct@reponomics.org) for conduct reports.

Badge Buddy starts the [Best Practices MCP](https://github.com/reponomics/best-practices-mcp) server, which is a separate project. Report a vulnerability in the server under [its security policy](https://github.com/reponomics/best-practices-mcp/blob/main/SECURITY.md). A fix there reaches Badge Buddy users through a Badge Buddy release that raises the pinned server version.

## Coordinated disclosure

The maintainer acknowledges each report within 14 days and keeps the reporter informed while it is assessed and fixed. The project aims to release a fix and publish the vulnerability within 90 days of the report, and coordinates the publication date with the reporter. Earlier publication may be necessary if the vulnerability is already public or actively exploited.

Confirmed vulnerabilities are published as [GitHub security advisories](https://github.com/reponomics/badge-buddy/security/advisories), with the affected and fixed versions, how to tell whether a system is affected, and how to remediate it. A CVE is requested through GitHub when appropriate, and the fix appears in the [changelog](CHANGELOG.md).

## Dependency and code scanning findings

OSV-Scanner and Dependabot report known vulnerabilities in dependencies, and CodeQL reports security weaknesses in the code. OSV-Scanner runs against the resolved dependencies of the pinned MCP server on pull requests and weekly. Vulnerabilities in existing dependencies and other security findings are fixed according to their severity, counted from when they are reported:

| Severity | Fixed |
| --- | --- |
| Critical or high | Before the next release, and within 30 days |
| Medium | Within 90 days |
| Low | At the maintainer's discretion |

No release is published while a critical or high finding is open. A finding that does not affect Badge Buddy may be suppressed only with a recorded reason, given in the code scanning dismissal or the scanner's ignore entry.

## Supported versions

Each release is supported until the next release is published. Support covers bug fixes and security fixes, which are delivered in a new release; once a newer release exists, earlier releases receive no further updates, including security updates. The project does not provide long-term support for older versions. Reports should identify the exact affected version.

# Skill evaluation methodology research

Research recorded 2026-11-20. This document separates observed repository practices, official product guidance, and proposed uses in Badge Buddy. No paid evaluations were run during this research. The Inspector checkout was inspected without installing or executing its project code.

## Why Inspector is the primary methodological reference

The maintainer identified MCP Inspector's per-skill evaluations and detailed discussion of their design as a useful example of disciplined agent-driven development. Its [contribution policy](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/CONTRIBUTING.md) explicitly describes a prompt-driven, AI-assisted workflow. That is direct evidence of the development approach, not a quantified audit proving what proportion of every historical line was written by an agent.

Research inspected main commit `eb54b447e5377a7a18acaea9602fced5cb4c5b9f` and development branch revision `7df76f6eea9ea425891289333837878ebb31ae6a`. The evaluation documentation, runners, and cases were unchanged between those revisions. Links below pin the inspected main commit so later changes do not silently alter the evidence behind these notes.

There are eleven development skills, ten with per-skill `evals/evals.json` files executed by a shared runner. The remaining development skill is intentionally user-invoked. Model-invoked skills require distinct positive cases and negative coverage. Structural checks validate the manifests/case declarations but do not claim that valid files establish model behavior. See [skill maintenance rules](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/AGENTS.md#maintaining-the-skills), [manifest checks](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/scripts/lib/skill-manifest.mjs), and [the pinned CLI validator runner](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/scripts/verify-skills-cli.mjs).

## What the methodology measures

The central reading is [Writing a skill and its eval cases](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/docs/skill-authoring.md). Its useful lessons include:

- First-turn selection, eventual invocation, and successful task completion are different observations.
- A handoff prompt can accidentally contain the destination skill's own trigger, allowing direct selection without using the first skill's guidance. Their worked example lost much of its apparent success after that cue was removed.
- A skill can load reliably while providing the wrong procedure. Invocation success is therefore insufficient evidence of usefulness.
- Distinct prompts broaden coverage; repetitions measure variation for each prompt. More prompts do not replace repeated trials.
- Resident instructions may already answer a case, and a neighboring skill may be the correct selection. Interpret misses before tuning descriptions.
- Skills compete for selection. Rerun the broader suite after description changes rather than checking only the edited skill.

These are reasons to inspect what a measurement means, not merely optimize its reported rate. The document includes imperfect historical results rather than presenting the system as universally successful.

The [shared runner](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/scripts/skill-eval.mjs) observes actual `Skill` events in fresh headless sessions. First-move cases have a one-turn budget; multi-step handoffs have a larger budget and require ordered skills in different assistant turns. Parallel calls do not establish that one skill's content led to the next. Repeated samples and separate rates distinguish these conditions and different agents. The project's thresholds are empirical choices, not general standards to copy unquestioningly. Negative cases can detect unwanted activation elsewhere in the skill set even when a run is filtered to a particular skill.

Examples: [testing skill cases](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/.claude/skills/testing/evals/evals.json) and [test-server handoff cases](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/.claude/skills/test-servers/evals/evals.json).

## The shipped mcpdo skill: behavior rather than invocation alone

Inspector's end-user `mcpdo` skill has a separate [behavioral harness](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/scripts/skill-eval-mcpdo.mjs). It evaluates the distributed skill outside the Inspector checkout, excludes eval data from the copied skill payload, uses the real CLI and test server, and isolates connection/storage state per sample. A PATH recording shim captures parsed command arguments, exit codes, and output. Failed samples preserve diagnostic artifacts.

The [structured matchers](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/scripts/lib/mcpdo-eval-matchers.mjs) accept equivalent command spellings rather than requiring the agent to reproduce one exact shell string. [Behavior cases](https://github.com/modelcontextprotocol/inspector/blob/eb54b447e5377a7a18acaea9602fced5cb4c5b9f/clients/mcpdo/evals/evals.json) cover choosing the correct server/tool/arguments, authentication handoff and resume, and operations that must not have succeeded before authentication. This is a useful model for checking what an agent actually did while allowing legitimate variations in its approach.

The harness documents practical limits: contributor-level configuration can still influence the external project, command-prefix approvals are not a security sandbox, and the behavior shim is POSIX-only. Infrastructure errors are distinguishable in artifacts but can still appear as misses in summaries. Research found no committed latest full-suite result artifact establishing a universal pass. Keep those limitations attached to any claim about the observed methodology.

## Layers to carry into Badge Buddy

| Layer | Question | Suitable evidence |
| --- | --- | --- |
| Structural validation | Are the plugin and cases well formed? | Schema, link, manifest, and deterministic case checks |
| Skill selection | Does a realistic request select the relevant skill without over-triggering? | Fresh natural prompts, near-miss negatives, actual invocation events, repeated trials |
| Handoff | Does one skill's guidance lead to the relevant next skill or reviewer? | Turn-aware traces and task context without answer/trigger cue leakage |
| Execution | Does the agent use the intended interfaces correctly? | Actual MCP requests, CLI arguments/results, saved state, and error paths |
| Outcome | Is the application or proposed change accurate and useful? | Artifact assertions, factual/rubric review, reference adjudication, and user effort |

Our [badge evaluation document](../../tests/badge-skill-evals.md) describes intended behavioral scenarios. Development-run records are kept privately and are not independent evidence of reliability. The [engineering scenarios](../../tests/engineering-skill-evals.md) are also specifications. Evaluation claims need an explicit methodology and review before publication.

For Scorecard, inspect actual MCP routing, direct CLI diagnostics, saved evidence, missing-binary behavior, and partial failures. A final answer claiming that a scan ran is insufficient. For Passing applications, capture the draft before review, review context/feedback, and revised draft; keep editorial peer review separate from oracle-aware grading. Preserve failure evidence and distinguish environmental failures from model behavior.

## Official Claude guidance: a separate tool assessment

Official [skill guidance](https://code.claude.com/docs/en/skills#evaluate-and-iterate-on-a-skill) distinguishes activation from output quality and recommends fresh contexts. [Anthropic's agent-evaluation discussion](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) describes tasks, repeated trials, traces, graders, and final environment outcomes as distinct objects. These principles support the measurement layers above; they do not establish the quality of a particular closed implementation.

The [native plugin-eval documentation](https://code.claude.com/docs/en/plugin-evals) describes `claude plugin eval` with repetitions, no-plugin comparison, MCP mocks, tool/file/trace graders, reports, and CI thresholds. Research verified that the installed Claude Code 2.1.327 exposes the command's help, but did not run it. Use `--no-publish` for private work because supported accounts can publish reports automatically. Real MCP processes and scaffold scripts require separate consideration from the agent's shell sandbox. There is no documented custom-code grader; deterministic parser and contract tests remain independent. A no-plugin arm measures the whole plugin's contribution, not only wording changes. The command is an unselected candidate, not a recommendation based on vendor status or availability; evaluate its behavior and artifacts against our requirements before adopting it.

[Headless startup diagnostics](https://code.claude.com/docs/en/headless#fail-ci-when-a-plugin-or-mcp-server-doesnt-load) provide another useful contract: inspect loaded plugins, configuration errors, and MCP startup state rather than equating process success with a working integration.

The open [skill-creator implementation](https://github.com/anthropics/skills/tree/main/skills/skill-creator) uses another evaluation format. Its [trigger runner](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_eval.py) observes activation events, while its [optimization loop](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_loop.py) separates training and held-out queries. These are useful implementation references, but their cases are not automatically interchangeable with native plugin eval suites. Recheck mutable official documentation and source when selecting a runner.

## Decisions and next steps

Adopt Inspector's measurement distinctions and diagnostic discipline as design requirements. Do not automatically copy its large bespoke runners or automatically replace them with Claude's native tool. Compare candidate runners on observable traces, reviewer control, real CLI/MCP support, isolation, repeatability, failure artifacts, cost accounting, and the ability to grade outcomes with our own deterministic code.

Keep the full Passing benchmark separate from fast plugin validation and Scorecard contract tests. Begin with one transparent historical remote fixture and one reviewed attempt, then expand model pairs, repetitions, masks, and cases after the workflow and grading are sound. The evaluation plan records the maintainer's chosen scope; this research does not authorize model runs, fixture publication, or changes to the user's live applications.

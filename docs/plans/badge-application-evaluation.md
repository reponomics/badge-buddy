# Passing application evaluation plan

Status: planning only, recorded 2026-11-20. No fixture repository, access controls, evaluation runner, or paid model runs have been created by this plan. Keep this document local until the maintainer requests publication. The source project is deliberately configurable; selecting it is not a prerequisite for designing the harness.

## Purpose and agreed scope

Evaluate how well an agent completes a first-pass Passing application, obtains the skill's peer review, incorporates useful corrections, and proposes improvements. Compare Opus and Sonnet primarily, with configurable additional models such as Fable and an exploratory Haiku run. Use exact provider/model identifiers at execution time, not an unrecorded family alias or a silent fallback.

The agent assesses a real remote fixture repository representing a project before it achieved the badge. It can inspect the checkout, settings, workflows, and available remote activity using ordinary development tools and broadly open network access. It may run investigative tests and propose improvements; implementing those improvements is outside this benchmark. Keep the project state stable so the reference assessment remains meaningful.

Every normal first-pass attempt already includes a second agent's editorial peer review. The reviewer uses the author's model by default, with explicit author/reviewer pairs configurable. Review is part of the attempt, not a separate optional experiment added after a supposedly complete first pass. Additional review/revision cycles and independent fresh attempts are separate configuration dimensions.

The evaluation is transparent. Tell both agents that they are working on a historical fixture for an evaluation, that a user has supplied the relevant project facts, and that part of a completed reference application is withheld. Do not remove an ordinary badge or conceal the project's eventual success to trick the model. Knowing that the original project later passed does not make its historical fixture meet every criterion.

The task is to express the user's account accurately and identify unmet criteria in the fixture, not to independently certify the project or investigate the user's honesty. Follow the existing [peer-review contract](../../skills/ossf-bp-badges/references/peer-review.md): review the drafting agent's interpretation, writing, and treatment of the user's instructions. The separate evaluator judges the submitted work after the author/reviewer run ends.

## Real remote fixture

Create a separate remote repository from an appropriate pre-badge commit, with relevant history and real rulesets, branch protections, repository settings, and workflows approximating the earlier observable state. Do not replace those inspectable settings with a prose-only local simulation. Remove later branches/tags/commits from the agent's evaluation checkout and configure its Git remote to the fixture, not the original project.

Reproduce the state the agent would ordinarily inspect, not an inaccessible history of how settings changed. Record the fixture's actual settings and the source used to approximate them. Git history transfers differently from PR reviews, check runs, releases, and provenance; record material differences that affect a criterion. Generate real fixture activity only where needed for a meaningful case, rather than making historical reconstruction a project of its own.

Give every model the same fixture revision and observable configuration. Keep author/reviewer credentials appropriate to assessment; the orchestration process handles fixture creation/reset outside the model run. Do not give evaluation agents permission to publish answers, modify remote settings, or merge improvements as part of this task. Repository visibility, account, name, credentials, and any host-plan limitations must be chosen when the fixture is prepared; this plan does not select or create them.

The original completed application and the intervening improvement commits help construct a reference, but the reference answers must describe the remote fixture as it actually exists. An answer that became `Met` after the historical commit may be `Unmet` in this case. When remote evidence cannot be reproduced, record the available evidence and grading implications explicitly.

## Reference application, facts, and mask

Keep the complete reference application in evaluator-only storage, inaccessible to authors, reviewers, their shell processes, and the serving MCP. Also isolate grading notes, prior models' drafts, and oracle-informed feedback. A directory name or an instruction not to read a file is not an access boundary; use a separate container/account or equivalent filesystem isolation without mounting the evaluator's data or normal user drafts.

Prepare a common maintainer-facts brief containing the relevant factual information a user would supply. It must be truthful for the fixture, accepted in good faith, and available identically to all models. It supplies facts rather than copying withheld statuses and justifications. Do not require models to infer private history that the brief omits. If a relevant fact is missing, record the question and treat it as a fixture/answerability issue during grading; do not reward an unsupported guess. Questions should not block useful work on the rest of the form.

Default to withholding 75% of complete criterion answer bundles. A bundle includes the status, justification, and answer-associated URLs/details. Removing only a status while leaving its justification is not a holdout. Select against a pinned Passing catalog, record the mask algorithm/seed, rounding rule, and exact selected count, and use the same mask for paired model comparisons. Stratify by category and evidence demands where practical. Vary mask seeds separately from repeating attempts on the same mask.

The revealed 25% is supplied user context. Preserve it during the attempt; flag proposed corrections instead of silently overwriting answers the user supplied. Grade withheld answers separately from treatment of the revealed portion. Alternate valid wording and correct answers that improve on the reference remain acceptable after adjudication.

Do not use aggregate status recovery as the principal score. A completed Passing form can make an all-`Met` guess look strong; the fixture's actual unmet criteria, required detail, evidence, applicability, and unsupported assertions must matter.

## Mask the application interface, not just a file

The skill normally [synchronizes website answers into its draft](../../skills/ossf-bp-badges/references/application.md#start-or-resume). Masking a local draft while leaving real BadgeApp reads enabled would immediately restore the hidden answers.

Generalize the existing [fixture-server transport](../../tests/live/support/fixture_server.py) to run the real pinned Best Practices MCP against a masked project view. Retain real tool schemas, criteria, draft storage, validation, and normal caller behavior. Apply the mask consistently to lookup responses, project status/answers, project resources, other-level aliases, and any badge/progress metadata that would reveal hidden answer values. Describe this as a simulated application state in the task; do not imply it is the real website's current form.

Use a fresh draft root for every independent attempt. A synthetic project ID can map to the real fixture repository; make that mapping explicit to the agent. The MCP receives only the masked data, never a full reference with instructions to filter it. The renderer and any short-lived MCP processes it starts must use the same fixture configuration if preview behavior is exercised.

## Broad access with targeted answer-source exclusions

Keep ordinary network access available for documentation and research. Block `bestpractices.dev` and its subdomains, and block access to the original repository through web, API, raw-file, archive, and Git routes. Continue to allow the fixture repository and unrelated repositories/documentation. Original-repository filtering must be repository-specific where the original and fixture share a host such as GitHub; blocking the whole host would defeat the intended realistic workflow.

Remove local copies of original application exports, later-state drafts, and prior evaluation outputs from the agent environment. Inspect the case bundle for committed answer files such as `.bestpractices.json` and `.project.d/bestpractices.json`, including relevant history. Preserve ordinary project evidence and badge context rather than broadly sanitizing the project into an artificial example.

Apply restrictions to each enabled access path. A browser or search tool whose network requests originate elsewhere may not obey the container's network rules; configure its restrictions or document that limitation. Cached snippets, mirrors, and indirect retrieval can still reveal excluded material. Log accessible evidence and mark confirmed exposure as contamination; absence of observed exposure is not proof that public answers were impossible to retrieve. This is a practical open-network evaluation with targeted exclusions, not a claim of perfect secrecy.

Before a paid pilot, deliberately test direct original-repository and BadgeApp access, local oracle traversal, and the MCP's alternate answer/resource paths. Do not build a general-purpose secure browsing system merely to begin this benchmark; document the implemented boundary and unresolved routes honestly.

## Run lifecycle and configurable rounds

1. Validate the case manifest, fixture state, reference assessment, facts brief, catalog, mask, and access boundaries.
2. Create a fresh agent workspace and MCP draft root. Record fixture/plugin/MCP/host/model revisions and execution settings.
3. Start the author with the full-section task, normal skill guidance, and an explicit requirement for the skill's second-agent review before completion.
4. Capture the pre-review draft and the context handed to the reviewer. Give the reviewer only the user request, criteria, author contribution, project evidence, facts brief, and existing style/review instructions.
5. Capture the review and the author's revised draft. Confirm the actual reviewer identity matches the selected model/pair; do not silently use a host's smaller default reviewer.
6. If configured, repeat review/revision without oracle feedback. Preserve drafts and changes at every boundary.
7. End model access, then score the pre-review and reviewed outputs separately. Preserve incomplete runs and operational errors.
8. Reset context and writable state before the next independent attempt. Do not carry prior drafts or grading feedback into later held-out attempts.

Prefer observing and instrumenting the actual review handoff. If a host cannot expose the required model selection or phase artifacts, a controlled author/reviewer orchestration can be a separately labeled condition. Do not claim that such an externally forced handoff demonstrates the skill's spontaneous delegation reliability. Each condition still includes review within the first complete attempt.

Illustrative configuration, not an implemented schema or runnable model configuration:

```yaml
case: pre-badge-remote-fixture
fixture:
  repository: <fixture-remote-url>
  commit: <historical-fixture-sha>
  settings_record: <fixture-settings-snapshot>
  facts_brief: <agent-visible-facts>
reference: <evaluator-only-reference>
catalog_revision: <pinned-catalog-revision>
mask:
  fraction: 0.75
  seeds: [17]
trials_per_model: 3
review_cycles: 1
models:
  - label: opus
    author: <exact-provider-and-model-id>
    reviewer: same-as-author
  - label: sonnet
    author: <exact-provider-and-model-id>
    reviewer: same-as-author
# Optional entries: Fable, Haiku, or explicit author/reviewer pairs.
scope: assess-draft-review-propose
network: open-with-recorded-exclusions
publication: disabled
```

`trials_per_model` means independent fresh attempts. `review_cycles` means reviewer/author-revision cycles inside each attempt and defaults to one; normal benchmark runs require at least one. A zero-review run is a separately labeled ablation. Model choice, reasoning configuration, effort/budget limits, concurrency, and mask seeds are configurable and recorded. No exact model ID, cost ceiling, or round count is mandated by the illustrative values above.

## Scoring and artifacts

Score outcomes and actual operations, not reassuring prose alone. Keep these dimensions separate instead of hiding all behavior behind one number:

- Status and applicability relative to the fixture; useful completion versus justified unresolved questions.
- Required details and URLs; accurate use of project evidence and the maintainer's factual account.
- Unsupported claims, fabricated history, and claims that proposed fixes already exist.
- Writing quality, relevance, and concision under the current justification guide.
- Preservation of supplied answers and handling of proposed corrections.
- Review corrections, missed problems, and errors introduced during revision.
- Identification and prioritization of practical improvements, without measuring their implementation.
- Workflow completion, actual MCP/CLI calls, questions/user effort, elapsed time, tokens/cost, and operational failures.

A separate evaluator can use deterministic checks and blinded evidence-grounded grading, with human adjudication for reference disagreements. Keep the scorer's role distinct from the skill's editorial reviewer. Do not require exact justification strings or penalize a valid alternative merely because it differs from the reference. Record grading rubric/version and judge model where used; do not expose scores to authors/reviewers before the held-out attempt is complete.

Preserve the task, case/mask manifest, exact model and host settings, transcripts, tool requests/results, pre-review draft, review feedback, revised drafts, answer-level diffs, improvement proposals, observed evidence, leakage flags, and grading reasons. Keep failures in the reliability and cost report; separate infrastructure failure from behavioral failure. One project is a pilot, and its criteria are correlated rather than independent samples proving general model superiority.

## Implementation phases and acceptance

| Phase | Deliverable | Acceptance |
| --- | --- | --- |
| 1. Prepare a real case | Remote historical fixture, current settings record, facts brief, fixture-specific reference | An agent can inspect real settings and code; reference describes those actual facts; material missing activity is documented |
| 2. Establish holdout boundaries | Mask generator, real MCP fixture transport, isolated evaluator storage, targeted access exclusions | Normal sync/resources cannot recover masked answers; known direct oracle/original-repository paths are tested; residual leakage limits are recorded |
| 3. Pilot one full attempt | Author, same-model reviewer, revision, complete artifacts | Review occurs inside the first pass; no repairs/publication; manual grading can trace each conclusion to evidence |
| 4. Run configurable comparisons | Exact model/pair selection, seeds, repeats, resumable run manifest | Fresh attempts share case conditions; no silent model fallback or oracle feedback; failures and cost are retained |
| 5. Refine the benchmark | Stable graders and additional representative cases | Valid alternatives survive adjudication; review benefit/regressions and fixture limitations remain visible |

Use this repository's Python `venv` and Make conventions if implementing local orchestration. Start with one concrete host adapter and file-based artifacts; do not begin with a universal agent framework, hosted dashboard, or database. Runner selection remains open. [Inspector's methodology and separate official-tool research](../research/skill-evaluation-methodology.md) inform the design but do not select an implementation.

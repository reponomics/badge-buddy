# Working with the badge application

Read the section for the operation requested. Tools named below belong to the plugin's `bestpractices` MCP server and appear under the host's prefix. Consult their descriptions and schemas for arguments, results, and errors. Keep the selected project consistent throughout the workflow.

## Start or resume

Keep all badge sections of a project in its MCP draft, and briefly tell the user where progress is saved using the reported `location`. If the user asks to work from a `.bestpractices.json` kept in a repository, or to reuse another project's answers, read [Repository file](#repository-file) before continuing; do not suggest that arrangement otherwise.

When beginning or resuming draft work in a session, find the project and synchronize the draft with the website for the level being worked on:

1. `find_project(query)` with the repository's URL, or the numeric ID when it is known. The tool returns candidates and does not choose between them. Continue with a single candidate whose `repo_url` is the repository; ask the user when several match; for none, see [Before registration](#before-registration).
2. `get_project_status(project_id)` to orient the session around the project's current progress.
3. `get_project_answers(project_id, level, statuses=["Met", "Unmet", "N/A"])` for the answers saved on the website at that level. Criteria the website reports as `?` are unanswered and need no draft entry.
4. `read_draft(project_id)` for the local draft. If none exists, start it with the saved answers in the next step.
5. `update_draft(project_id, changes)` with the saved status and justification of every criterion the draft does not yet answer. A criterion the draft records as `?` counts as unanswered; say so when the website's answer replaces one. Leave every other draft answer as it is, including one with an empty justification.

After synchronization the draft is the working assessment: the website's saved answers plus the user's local changes. Report the fields where the draft and the website differ. A differing draft answer is either work not yet transferred or a website change made since it was drafted; resolve it using the user's current answers, asking only about differences that remain unclear. The same status with different wording is a wording update; keep the intended wording for a later transfer. Synchronization only adds to the draft. A draft answer may be work that has not been saved to the website yet, so never overwrite one with the website's value unless the user chooses that.

Retain the verified repository and project association for the session, and find the project again if either changes. A failed lookup, such as `upstream_unavailable` or `rate_limited`, does not establish that the project is unregistered; repeat it before concluding that. Synchronize another level when the user starts work on it.

Synchronization copies saved answers and reports differences. It does not establish that the project meets each criterion.

The public data contains only saved answers. If a section has never been saved, explain that its edit-page suggestions and percentage are not visible to the server, and suggest saving that page once before synchronizing again. Site-generated suggestions may have incomplete justifications even when their status is correct.

Each website read is a live request, limited to one per second. Draft operations are local; assume no outside edits to the website during the session. Synchronize again after website changes are saved or when requested. A failed read leaves the draft as it was and does not establish the current website state.

A readable copy of a level, with each criterion beside its saved answer, is published as the resource `project://{project_id}/{level}`, or `project://{project_id}/{level}/{category}` for one category. Use it to show saved answers in the conversation or to give a reviewer context.

### Before registration

When `find_project` returns no candidates, link to [registration](https://www.bestpractices.dev/projects/new); it happens on the website. If the user chooses to defer it, continue without asking again.

Criteria lookups need no project. The project tools do, so until an entry exists, keep the answers in a JSON file of your own: start from `{}`, apply changes with `build_draft(draft=<document>, changes=<fields>)`, which stores nothing, and write the returned `draft` to the file. Unless the user chooses another place, keep the file in the plugin data directory, named for the repository, and tell them where. Check each answer against the status, justification, and URL rules in its full criterion record; `validate_draft` and proposal URLs become available after registration.

After registration, find the new entry and record the file's answers with `update_draft`.

## Record answers

Help the user carry their decisions into the form. Here, confirmed changes are changes the user has requested or agreed to; they do not need the assistant's certification.

Send confirmed changes through `update_draft(project_id, changes)`. Apply status and justification together when both change; a wording-only update changes only the justification.

Then call `validate_draft(project_id, section)` for the section being worked on: reused Metal identifiers can have different requirements at each level. A finding may concern an answer copied from the website; mention it without treating it as one of the user's changes. Explain the specific format or required-detail issue and help resolve it without adding a separate compliance audit or making validation a condition of saving progress.

An open preview does not add an approval step for an exact change the user has already requested. Apply it to the draft. Use a separate preview revision only when the user wants to consider wording before adopting it.

## Preview

The board is a local page that the plugin's renderer writes from a draft file. The renderer starts the MCP server briefly to read the section's criteria, so it needs the same `uvx` setup as the tools. It sends nothing to BadgeApp and changes no answers. Offer once to open the board when starting or resuming application work.

```bash
python3 "<board-renderer>" --input "<draft-file>" --output "<board-html>" --project-id "<project-id>" --section baseline-1 --view all
```

Use the renderer path resolved by the skill and replace the other placeholders. `--view overview` opens the Overview and `--view all` shows every criterion with its answer. Add `--open` to open the browser; the command prints the file URL either way. Write the HTML to session scratch space, one board per requested section. For work before registration, `--project-id` accepts a short label in place of the ID.

Use the stored draft's `location` as the input, or the working file when the answers are kept outside the stored draft. The renderer only reads its input; change the stored draft through `update_draft`, never by editing that file. Criteria the draft does not answer appear as unanswered.

Run the renderer again after the answers change. An open board reloads within five seconds and retains its selected view. It displays the server's criterion text with stable numbering, so filtered lists may have gaps. Metal criteria are grouped by the form's sections, in the form's order. Browsing neither approves answers nor copies them into the repository.

When the user requests a preview of wording they have not adopted:

1. Copy the board's input to a temporary revision file and render the board from that file.
2. Change only `<criterion>_justification` in the revision, leaving its status and therefore its board category unchanged; explain that distinction once. To check the wording against the intended response, pass a document containing that criterion's intended status and the wording as `draft` to `validate_draft`.
3. When the user approves the wording and response, record the exact approved status and justification with `update_draft`, or in the working file, and render the board from the normal input again. The board category updates in place.
4. On cancellation, pause, or transfer preparation, discard unfinished revisions and render the board from the normal input.

Initial drafts can apply status and justification together. Wording-only revisions keep the same status. Never export unfinished preview wording.

## Export

The draft is already a valid `.bestpractices.json`. For a local JSON export, copy the stored draft from its `location` to the requested path. Nothing is fetched. If the destination is inside the repository, follow the writeback steps in [Repository file](#repository-file).

## Website transfers

Answers reach the website through a proposal URL: the user opens it, reviews the proposed changes highlighted in the official edit form, and saves. Generating the URL saves nothing.

Use the draft and the selected project ID. Finish or discard outstanding preview revisions first. Mention unanswered criteria and unresolved differences from the website without requiring a completed badge or another assessment. Offer an All criteria preview if the user has not already reviewed the answers being transferred. After the form is filled, follow [Saving on the website](#saving-on-the-website) to explain the save action and confirm the result afterward.

Two kinds of edit cannot be proposed. A proposal URL cannot reset a saved answer to `?`: the form ignores a proposed `?`, with or without an override, although BadgeApp's documentation says otherwise. Wording too long for a URL cannot be carried either. For both, the user edits the form directly; give them the exact value for each field. Do not suggest a browser console script for these edits. If the user asks for one, say once that it runs generated code in their signed-in session, then write a script that sets only the named fields and saves nothing.

BadgeApp can also import answers from a file committed to the project's repository. It can start a new entry from another project's answers, and it cannot replace answers that are already saved. Describe it when the user asks about it or already keeps such a file; see [Repository file](#repository-file).

### Proposal URLs

Call `prepare_update_url(project_id, section, draft, overrides)` after resolving differences from the website, using the selection below.

The server puts every valid field of the section into the URL, including values equal to the saved ones, and a synchronized draft contains the whole section. Propose only what differs: read the saved answers again, collect the draft fields of the section whose values differ from them, keeping each criterion's status and justification together, and pass that subset as `draft`. Leave out `?` statuses, which the form ignores. If nothing differs, say so instead of generating a URL. A narrower selection the user asks for is passed the same way. With `section` set to `choose_section`, the URL keeps the fields of every level and the user picks the level on the site.

Use the narrowest `overrides` mode that covers what the user asked to change.

If the user prefers a website value, adopt it in the draft before generating the URL. Site-generated suggestions need not displace answers the user has approved.

The form applies proposals as follows:

| Existing value | Proposal | Result |
| --- | --- | --- |
| Blank or unknown status | Known status | Applied, highlighted yellow. |
| Known status | Different status without a matching override | Retained; difference highlighted blue. |
| Known status | Different status with a matching override | Replaced, highlighted orange. |
| Matching status, blank justification | New justification | Applied. |
| Matching status, existing justification | New wording without a matching override | Existing wording retained. |
| Matching status, existing justification | New wording with a matching override | Wording replaced. |
| Any status | `?` | Status proposal ignored, even with an override. |

Forcing a status also forces its justification. A blocked status change blocks its accompanying justification even if that justification has a separate override. The site applies the overrides; generating a URL does not establish that an override matched or that the form was saved.

Relay the result's outcome and warnings, and explain any requested field that was not encoded using its reported reason.

The server returns a single URL with its `encoded_size_bytes` and neither splits nor limits it. Requests near 8 KB have been rejected in practice; above about 6,000 bytes, divide the differing answers among several `draft` documents and have the user save each page before opening the next. Wording too long for one URL is entered in the form directly.

Proposals survive login redirects and apply after initial site suggestions, but a draft recovered after login takes precedence. Revisiting a URL reapplies its proposals. The site trims surrounding whitespace from proposed justifications. If the form behaves differently, use direct form editing for the requested changes.

### Saving on the website

Explain that both **Save (and continue)** and **Submit (and exit)** save the entry; the latter simply leaves edit mode. There is no irreversible completion step: entries are public from registration and remain editable.

The user reviews and saves the form, or explicitly asks Claude to log in or save it; carry out that request when given. The server neither authenticates nor writes to BadgeApp. Saving can reapply the site's high-confidence automated answers, and URL overrides do not disable this. If an answer changes again, inspect the site's explanation and help address the relevant project condition.

After the user saves, confirm the result with `get_project_answers`, passing the changed criteria as `criterion_ids`, and compare the returned values with the draft. Preparing or opening a URL does not change the saved answers.

If the user asks about the license of their BadgeApp entry data, consult “Privacy and legal issues” on the [site's front page](https://www.bestpractices.dev/en), because the terms depend on when the entry was last edited.

## Repository file

BadgeApp can read answers from `.bestpractices.json` at the top of the project's repository, or from `.project.d/bestpractices.json`; it checks them in that order. The file is mostly used to carry answers from one project to a new one: committed to the new repository, it fills the new entry's unanswered criteria when each section is first edited. For an entry that already has answers, it has these limits:

- The site reads the file from the remote repository, so a change has no effect until it is committed and pushed.
- Imported values fill unanswered criteria and show differences. They cannot replace an answer that is already saved; that requires a proposal URL with `overrides`.
- The server shares the file's format but does not read, write, or send it. Read its `guide://repository-file` resource before advising on the import; it describes how BadgeApp uses the file at the revision the server follows.

Support the file when the user asks for it or already keeps one, and use proposal URLs for everything else.

### Reuse another project's answers

Each answer in a copied file describes the project it came from. Before the file is committed to the new repository, go through it with the user: keep the answers that hold for the new project, correct or drop the others, and replace URLs that point to the source project. Remove `id` and `repo_url` if present; they identify the source entry.

The same answers can be proposed without committing a file: once the new project is registered, pass the reviewed document as `draft` to `prepare_update_url` for the new project's ID, or record it with `update_draft`.

### Work from the file

When the user wants their answers kept in the repository file instead of the stored draft, copy the existing file to a temporary working file and retain the original bytes or digest for writeback. If direct edits are already authorized, use the repository file itself. The file must contain a flat JSON object.

The working file then takes the place of the stored draft on every operation; this work has no additional stored copy. Apply changes with `build_draft(draft=<document>, changes=<fields>)` and write the returned `draft` to the working file. Pass the document as `draft` to `validate_draft` and `prepare_update_url`. Synchronize it as in [Start or resume](#start-or-resume), adding saved answers through `build_draft`.

Before writing a temporary working file back to the repository, show the changes or preview and obtain agreement unless already authorized. Compare the destination with the retained original; for a new file, check that the destination has not appeared. Reconcile any intervening changes rather than overwriting them. Copy the agreed file. Tracking a new file in Git, committing, and pushing are separate user choices.

### Import by the website

The site reads the file when editing an unsaved section, on `reanalyze=1`, and on **Save (and continue)**. **Submit (and exit)** does not normally reread it. Changing the repository URL also triggers full analysis on save.

Use a flat JSON object within the 100,000-byte limit. Fields use lowercase IDs followed by `_status` or `_justification`; Baseline fields look like `osps_ac_01_01_status`. Unknown or invalid statuses, including `?`, are ignored.

The site also reads `security-insights.yml`; that format has its own specification, so do not infer its mappings from this JSON format.

## API

Use this section only when explaining or diagnosing an API, field-format, or tool issue; ordinary application operations use the server's tools.

BadgeApp serves a project as `GET /projects/<ID>.json` and matches `GET /projects.json?url=<encoded-url>` against homepage or repository URLs, ignoring trailing slashes and spaces. Public JSON may return Baseline display fields such as `OSPS-AC-01.01_status`; the server returns answers under the lowercase form names. Criterion lookups accept display IDs, while draft field names must be the lowercase form.

Proposal URLs use `/(:locale/)projects/:id/:section/edit?KEY=VALUE&...`, with URL-encoded values. Fields outside the edited section are ignored; `name`, `description`, `license`, and `implementation_languages` are accepted in any section. Known status values are `Met`, `Unmet`, and permitted `N/A`.

The upstream API supports authenticated writes but recommends proposals or repository JSON instead. Neither the plugin nor the server has an authenticated write path.

## Stop

Discard unfinished preview revisions and distinguish durable answers from proposals opened but not yet saved on the website, and from any repository file awaiting writeback. Apply or discard that work according to the user's instructions, then remove session scratch files, including boards. The stored draft remains; resume from it, and synchronize, next time.

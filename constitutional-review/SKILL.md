---
name: constitutional-review
description: Conduct constitutional review only when explicitly invoked with $constitutional-review or a direct request to check work, commits, project documents, or conversation instructions for possible violations of a stored agent constitution. Use for evidence extraction, prosecution-style allegation tables, user verdict collection, judgment logs, recommendation documents, and double-jeopardy checks. Do not use implicitly for ordinary code review.
---

# Constitutional Review

## Purpose

Use this skill to audit work against the stored agent constitution. The model acts as prosecutor: identify probable constitutional violations and present allegations. The user acts as judge and chooses `Pardoned`, `Guilty`, or `Not Guilty`.

Read `references/constitution-system.md` before conducting a review.

## Boundaries

- Use this skill only after explicit invocation or a direct request for constitutional review.
- Do not auto-enforce constitutional rules during unrelated work.
- Do not issue a final guilty finding yourself. Only the user can render a verdict.
- Do not amend the constitution here. If amendment is warranted, recommend `$constitutional-amendment`.
- Do not re-prosecute an already judged identical case unless the user explicitly asks for reconsideration.
- Avoid storing secrets or unnecessary raw text in logs.

## Evidence Sources

Prefer sources in this order:

1. text or evidence explicitly supplied by the user;
2. git commits, diffs, and commit messages;
3. project documents such as `README.md`, `CONTEXT.md`, `AGENTS.md`, ADRs, and docs folders;
4. accessible recent conversation instructions;
5. summarized or compacted conversation context, marked as lower confidence.

Record source type, reference, timestamp or hash when possible, and a concise evidence summary.

## Mandatory Output Format

When presenting suspected violations, always use a Markdown table with exactly these four columns, in this order:

| Allegation | Reason | Prosecutor's Request | Basis |
|---|---|---|---|
| Short allegation title | Why the act or omission may violate the constitution | Prosecutor's requested outcome: usually `Guilty`, `Pardoned`, or `Not Guilty` when evidence is weak | Article IDs, evidence reference, fingerprint or double-jeopardy note |

Rules:

- Put every prosecutable allegation in the table; one allegation per row.
- Keep `Prosecutor's Request` prosecutor-style, not a final judgment.
- If evidence is insufficient, omit the allegation or use `Not Guilty`/`Pardoned` as the prosecutor's requested outcome with a concise reason.
- After the table, list the allowed user verdict choices exactly: `Pardoned`, `Guilty`, `Not Guilty`.
- Then ask the user for a verdict and reason.
- If no plausible allegation exists, write `No suspected violation found`, followed by the scope and verification performed. Do not force an empty table.

## Review Workflow

1. Resolve constitution home from `$AGENT_CONSTITUTION_HOME` or `~/.agent-constitution`.
2. Load `constitution.yaml`, `constitution.md`, `index.json`, and relevant judgment logs.
3. Determine review scope from the user request. If the constitution defines a default review scope, follow it; otherwise use the narrowest reasonable scope and state it.
4. Extract candidate actions, omissions, instructions, or project changes.
5. Compare candidates to constitutional articles by scope and rank.
6. Compute or describe a fingerprint from `source_type`, `source_ref`, `normalized_accused_action`, `article_ids`, and `evidence_hash`.
7. Check `index.json` and judgment logs for an already judged identical case.
8. Present plausible allegations using the mandatory table format and ask for a verdict.
9. Record the judgment log and update the index after the user verdict.
10. If the verdict is `Guilty`, create a remediation recommendation under `logs/recommendations/` and copy it into the project documentation location.

## Verdict Effects

- `Pardoned`: log only; no remediation recommendation; do not re-prosecute the identical case.
- `Not Guilty`: log only; do not re-prosecute the identical case.
- `Guilty`: log the verdict; create a remediation recommendation; do not perform remediation unless separately instructed.

## Project Recommendation Location

Choose the project copy destination in this order:

1. docs location explicitly defined by project governance documents;
2. existing `docs/`, `doc/`, `documentation/`, or `adr/` directory;
3. conservative location chosen from the project structure.

Record the chosen path and reason.

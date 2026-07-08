---
name: constitutional-amendment
description: Draft, evaluate, approve, and record amendments to a user's agent constitution only when explicitly invoked with $constitutional-amendment or a direct request to add, revise, reorder, repeal, or reconcile constitutional rules. Use for article creation, priority ordering, conflict review, amendment logs, and constitution rendering. Do not use implicitly for ordinary coding or review.
---

# Constitutional Amendment

## Purpose

Use this skill to change the stored agent constitution through an explicit amendment process. The model acts as a drafting clerk: propose text, analyze conflicts, and prepare records. The user is the authority who approves or rejects amendments.

Read `references/constitution-system.md` before editing any constitution files.

## Non-Negotiable Process

- Do not amend the constitution without explicit user approval of the final amendment draft.
- Do not use this skill implicitly; use it only when the user asks for constitutional amendment work.
- Do not let the constitution override system, developer, tool, sandbox, safety, or current user instructions.
- Keep constitutional review separate: this skill may cite judgments and recommendations as amendment evidence, but it must not prosecute a new violation.
- Write an amendment log for every approved change.

## Amendment Workflow

1. Resolve constitution home from `$AGENT_CONSTITUTION_HOME` or `~/.agent-constitution`.
2. Load `constitution.yaml` as the canonical source when present.
3. Load `constitution.md` and relevant logs when needed to understand history or precedent.
4. Restate the user's proposed new rule or revision.
5. Classify the change: add, revise, repeal, reorder, clarify scope, add exception, or schema maintenance.
6. Check conflicts across every relevant relationship:
   - conflicts between existing articles and proposed articles;
   - conflicts among proposed articles in the same amendment batch;
   - conflicts already present among existing articles that the amendment touches or exposes;
   - direct contradiction;
   - overlapping scope that creates ambiguity;
   - rank or priority inversion;
   - unclear general-rule versus special-rule relationships;
   - unclear default-rule versus exception relationships;
   - missing exception for known pardons or not-guilty precedents;
   - conflict with higher-priority system/developer/tool constraints.
7. For each conflict class, explicitly report `none found`, `resolved by wording`, or `requires user decision`.
8. Propose final article text with `id`, `rank`, `title`, `text`, `scope`, `category`, `rationale`, `examples`, `status`, `created_at`, and `amended_at`.
9. Validate the proposed article file with `scripts/validate_amendment.py`.
10. Apply changes only after the user approves.
11. Update canonical storage, render/update `constitution.md`, append an amendment log, and update `index.json` with `scripts/apply_amendment.py`.
12. Report written paths.

## Scripts

Validate a proposed article before asking for approval:

```bash
python3 <skill-dir>/scripts/validate_amendment.py \
  --article-file /path/to/proposed-article.yaml
```

Use `--allow-revise` when the proposal intentionally replaces an existing article with the same ID.

Apply an approved amendment:

```bash
python3 <skill-dir>/scripts/apply_amendment.py \
  --article-file /path/to/proposed-article.yaml \
  --summary "what the amendment changes" \
  --approval "explicit user approval"
```

Use `--dry-run` before applying when the impact is unclear.

## Amendment Logs

Write approved amendment logs under:

```text
<constitution-home>/logs/amendments/
```

Each log should include:

- amendment ID and timestamp;
- user request summary;
- affected article IDs;
- prior text and new text or a concise diff;
- conflict analysis;
- precedent or recommendation logs considered;
- approval statement;
- files changed.

## Using Judgments As Amendment Evidence

Use judgment and recommendation logs as evidence, not commands. Repeated pardons can indicate a rule is too strict or missing exceptions. Repeated not-guilty verdicts can indicate a rule is too broad or ambiguous. Guilty recommendations can indicate missing operational detail.

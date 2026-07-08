# Constitution System Reference

## Authority

The constitution is a user-maintained local rule system for development and
agent-work practices. It is not higher than system, developer, tool, sandbox,
safety, or current user instructions.

Operational hierarchy:

1. system, developer, tool, sandbox, and safety constraints;
2. current explicit user instruction;
3. project instructions such as `AGENTS.md`, `README.md`, `CONTEXT.md`, ADRs, or local governance docs;
4. stored constitution;
5. judgment and amendment logs as precedent evidence.

During constitutional review, the constitution is the audit standard. During
ordinary work, it is not automatically applied unless the user explicitly
invokes a constitution skill.

## Storage

Use `AGENT_CONSTITUTION_HOME` when set. Otherwise default to:

```text
~/.agent-constitution/
```

Canonical files:

```text
constitution.yaml
constitution.md
index.json
logs/amendments/
logs/judgments/
logs/recommendations/
```

Use `constitution.yaml` as the canonical source when present. Use
`constitution.md` as human-readable output. Keep logs append-only when
practical.

## Scripted State Changes

Prefer bundled scripts for durable state changes instead of hand-editing logs or
indexes:

- use `constitutional-review/scripts/check_precedent.py` for double-jeopardy checks;
- use `constitutional-review/scripts/record_judgment.py` after the user gives a verdict;
- use `constitutional-amendment/scripts/validate_amendment.py` before asking for final amendment approval;
- use `constitutional-amendment/scripts/apply_amendment.py` after explicit approval.

The model still performs legal reasoning, evidence extraction, conflict review,
and user-facing explanation. Scripts own repeatable storage mechanics:
fingerprints, judgment IDs, index updates, recommendation archive creation,
amendment logs, and Markdown rendering.

## Article Model

Recommended article fields:

```yaml
id: C001
rank: 1
title: "Short title"
text: "Normative rule text."
scope:
  applies_to: []
  excludes: []
category: []
rationale: "Why this rule exists."
examples: []
status: active
created_at: "YYYY-MM-DD"
amended_at: null
```

Use `rank` for priority, but rely on scope, exceptions, and specificity to
resolve conflicts.

## Conflict Review

When amending the constitution, explicitly check:

- existing article versus proposed article;
- proposed article versus proposed article within the same amendment batch;
- existing article versus existing article when the amendment touches or exposes a conflict;
- direct contradiction;
- overlapping scope ambiguity;
- priority inversion;
- unclear general-rule versus special-rule relationship;
- unclear default-rule versus exception relationship;
- missing exception;
- conflict with higher-priority external constraints.

For each conflict class, report `none found`, `resolved by wording`, or
`requires user decision`.

## Case Identity

For double-jeopardy checks, identify an identical case by:

```text
source_type
+ source_ref
+ normalized_accused_action
+ article_ids
+ evidence_hash
```

Project path is metadata, not a core identity component.

## Verdicts

`Pardoned`: possible violation is acknowledged or left unresolved, but the user
closes the case without remediation. Log only. Do not create a recommendation.
Use as possible amendment evidence later.

`Not Guilty`: user finds no constitutional violation. Log only. Do not
re-prosecute the identical case. Repeated not-guilty results may indicate an
overbroad or unclear article.

`Guilty`: user confirms violation. Log the judgment, create a remediation
recommendation document, archive it under `logs/recommendations/`, and copy it
into the project documentation location. Do not perform remediation unless
separately instructed.

## Judgment Log Fields

Recommended fields:

```yaml
case_id: J-YYYY-MM-DD-NNN
fingerprint: sha256:...
source:
  type: git_commit
  ref: abc123
project:
  path: /path/to/project
accused_action: "Normalized allegation"
articles: ["C001"]
evidence_summary: "Concise summary"
prosecution_reason: "Why this may violate the constitution"
verdict: pardoned|guilty|not_guilty
verdict_reason: "User's reason when provided"
created_at: "ISO-8601 timestamp"
```

## Recommendation Document

For `Guilty`, write a Markdown recommendation with:

- case ID;
- verdict;
- violated articles;
- source evidence;
- violation summary;
- prosecutor recommendation;
- suggested remediation tasks;
- risk if unfixed;
- user verdict reason;
- archive path;
- project copy path and selection reason.

## Privacy Rules For Public Sharing

Do not publish live constitution stores, judgment logs, recommendation logs,
account identifiers, API keys, tokens, private project names, private paths, or
private commit history. Public examples should be synthetic.

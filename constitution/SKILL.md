---
name: constitution
description: Read and interpret the user's agent constitution only when explicitly invoked with $constitution or a direct request to read, summarize, or interpret the stored constitution. Use for constitution lookup, article explanation, scope clarification, precedent lookup, and constitutional storage inspection. Do not use implicitly for ordinary coding, review, planning, or policy advice.
---

# Constitution

## Purpose

Use this skill to inspect the stored agent constitution and explain how its
articles, precedents, amendment logs, and judgment logs apply. This is a
read-only skill: do not amend the constitution, prosecute violations, or create
judgment records here.

Read `references/constitution-system.md` before interpreting storage layout,
article fields, verdict effects, or precedent meaning.

## Operating Boundaries

- Treat the constitution as a user-maintained local rule system for work and development practices.
- Use this skill only after explicit invocation or a direct user request for constitutional lookup.
- Do not claim the constitution overrides system, developer, tool, sandbox, safety, or current user instructions.
- When current instructions conflict with the stored constitution, explain the conflict and the governing instruction hierarchy.
- Do not auto-enforce constitutional articles during unrelated work.
- Do not mutate `constitution.yaml`, `constitution.md`, `index.json`, or logs from this skill.

## Storage

Resolve the constitution home from `$AGENT_CONSTITUTION_HOME` or:

```text
~/.agent-constitution/
```

Expected storage:

```text
~/.agent-constitution/
├── constitution.yaml
├── constitution.md
├── index.json
└── logs/
    ├── amendments/
    ├── judgments/
    └── recommendations/
```

`constitution.yaml` is the canonical source when present. Treat
`constitution.md` as a human-readable rendering or mirror unless the user says
otherwise.

## Workflow

1. Locate the constitution storage root from `$AGENT_CONSTITUTION_HOME` or `~/.agent-constitution/`.
2. Read `constitution.yaml` first when it exists. Read `constitution.md` for human-readable context.
3. Read only the relevant logs or index entries needed for the user's question.
4. Explain articles by `id`, `rank`, `title`, `scope`, and practical effect.
5. Use `scripts/inspect_store.py` when the user asks for a storage summary.
6. If the user asks for amendment, switch to `$constitutional-amendment`.
7. If the user asks whether work violated the constitution, switch to `$constitutional-review`.

## Scripts

Inspect the stored constitution without modifying it:

```bash
python3 <skill-dir>/scripts/inspect_store.py
```

Inspect a custom constitution home:

```bash
python3 <skill-dir>/scripts/inspect_store.py --home /path/to/.agent-constitution
```

## Output

When answering, include:

- the article IDs or log IDs used;
- whether the answer is from the canonical constitution, a rendered document, or logs;
- any uncertainty caused by missing storage files or inconsistent records.

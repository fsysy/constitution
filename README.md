# Agent Constitution Skills

> My Codex was written by Codex.

This skill package helps Codex follow consistent, complex rules for your own
codebase. If a rule is simple and must always be obeyed, the most reliable place
for it is still `AGENTS.md`: always-loaded instructions are more predictable
than skills that depend on explicit or automatic loading. But project rules are
rarely simple forever. They change by context, by precedent, and by the shape of
the codebase, much like law changes in society. Agent Constitution gives those
rules a legal-style workflow: enact rules, review violations, record judgments,
and keep the system orderly without loading every rule into every task.

The main advantage is control. You can keep very detailed governance rules out
of the everyday token budget, then invoke them only when you want to clean,
audit, or steer a codebase. Your job is to register your working rules in the
constitution, review how they apply, and decide how they should shape your
projects. Build your own constitution, and give order to chaotic code.

The live constitution is private user state. This public package contains only
reusable skills, starter templates, scripts, and reference instructions.

## Install

Install the skills into your Codex home:

```bash
npx github:fsysy/constitution
```

By default, this copies the skills to:

```text
~/.codex/skills
```

Set `CODEX_HOME` to install into a different Codex home:

```bash
CODEX_HOME=/path/to/.codex npx github:fsysy/constitution
```

## Skills

- `constitution-init`: starts a project or local store that should be governed by
  a constitution from the beginning.
- `constitutional-amendment`: creates or revises rules through an amendment
  process.
- `constitutional-review`: reviews a codebase or change against the constitution
  and reports suspected violations.

## How It Works

### Amendment

Use `$constitutional-amendment` when a rule should be created, changed,
reordered, clarified, or repealed. The skill treats rulemaking like an amendment
process: it lists rules by importance, checks for conflicts with existing rules,
proposes clearer wording, and asks for explicit approval before writing the
change.

Example:

```text
$constitutional-amendment add a rule requiring verification notes in final reports
```

### Review

Use `$constitutional-review` when you want to check whether a codebase, commit,
document, or plan follows the constitution. The skill acts like a prosecutor: it
reports alleged violations article by article, explains the reason for
prosecution, and recommends a requested outcome.

You act as the judge. After reviewing the allegation, reason, requested outcome,
and basis, you decide the verdict: `Pardoned`, `Guilty`, or `Not Guilty`. The
judgment becomes precedent, and the system records how similar cases should be
handled later.

Example:

```text
$constitutional-review review the latest commit
```

### Init

Use `$constitution-init` when you want a new project or local governance store to
start under constitutional management. It creates the initial constitution files,
index, and log directories used by the amendment and review workflows.

Example:

```text
$constitution-init
```

## Direct Scripts

Initialize the default constitution store:

```bash
python3 constitution-init/scripts/init_constitution.py
```

Use a custom location:

```bash
python3 constitution-init/scripts/init_constitution.py --home /path/to/.agent-constitution
```

Overwrite existing `constitution.yaml`, `constitution.md`, and `index.json` only
when you intentionally want to replace them:

```bash
python3 constitution-init/scripts/init_constitution.py --force
```

Validate a constitution store:

```bash
python3 constitution-init/scripts/validate_constitution.py /path/to/.agent-constitution
```

Validation requires PyYAML.

## Constitution Home

By default, the private constitution store lives at:

```text
~/.agent-constitution
```

Set `AGENT_CONSTITUTION_HOME` to use a different location.

## Privacy Boundary

Do not commit live constitution state from `~/.agent-constitution` or any custom
`AGENT_CONSTITUTION_HOME` location. In particular, keep these private:

- judgment logs;
- recommendation logs;
- amendment history tied to private projects;
- account identifiers;
- private project paths;
- user-specific governance history.

## Repository Contents

```text
constitution-init/          Initialize and validate a private constitution store
constitutional-review/      Conduct explicit constitutional reviews
constitutional-amendment/   Draft and record approved amendments
bin/install.js              npx installer for Codex skill directories
```

## Notes

The constitution is advisory governance for the agent. It must not override
system, developer, tool, sandbox, safety, or current user instructions.

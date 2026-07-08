# Agent Constitution Skills

> My Codex was made with Codex, then gently subjected to constitutional review.

This repository contains a small public skill package for maintaining a local,
user-controlled agent constitution. It gives Codex a structured way to initialize
governance files, review work against them, and amend them with explicit user
approval.

The live constitution is private user state. This package contains only reusable
skills, starter templates, scripts, and reference instructions.

## Skills

- `constitution-init`: initializes or validates a private local constitution store.
- `constitutional-review`: reviews work against the stored constitution, presents prosecutor-style allegations, collects the user's verdict, and writes judgment logs.
- `constitutional-amendment`: drafts, evaluates, approves, and records constitutional amendments.

## Typical Flow

1. Install or expose this skill package to Codex.
2. Run `$constitution-init` to create a local constitution store.
3. Use `$constitutional-review` when you want a specific piece of work checked against the constitution.
4. Use `$constitutional-amendment` when a rule needs to be added, revised, clarified, reordered, or repealed.

By default, the private constitution store lives at:

```text
~/.agent-constitution
```

Set `AGENT_CONSTITUTION_HOME` to use a different location.

## Usage

### Initialize A Constitution Store

Ask Codex to run the init skill:

```text
$constitution-init
```

Or run the script directly:

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

### Validate A Constitution Store

Ask Codex to validate the configured store:

```text
$constitution-init validate my constitution store
```

Or run the validator directly:

```bash
python3 constitution-init/scripts/validate_constitution.py
```

Validate a custom location:

```bash
python3 constitution-init/scripts/validate_constitution.py /path/to/.agent-constitution
```

Validation requires PyYAML.

### Conduct A Constitutional Review

Invoke review explicitly. The skill is intentionally not automatic.

```text
$constitutional-review review the latest commit
```

```text
$constitutional-review check this PRD against my constitution
```

The review skill presents suspected violations as allegations. The user gives
the final verdict: `Pardoned`, `Guilty`, or `Not Guilty`.

### Amend The Constitution

Invoke amendment explicitly when a rule should change.

```text
$constitutional-amendment add a rule requiring verification notes in final reports
```

```text
$constitutional-amendment revise C009 so it allows documented non-git projects
```

The amendment skill drafts the change, checks conflicts, shows the impact, and
writes files only after explicit user approval.

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
```

## Notes

The constitution is advisory governance for the agent. It must not override
system, developer, tool, sandbox, safety, or current user instructions.

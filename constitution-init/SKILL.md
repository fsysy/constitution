---
name: constitution-init
description: Initialize, inspect, or validate a private local agent constitution store. Use when the user asks to create a constitution home, bootstrap constitution.yaml/constitution.md/index/log folders, install starter constitutional governance files, or validate an existing agent constitution setup.
---

# Constitution Init

## Purpose

Use this skill to create or inspect a local agent constitution store. The live store is private user state; do not publish it or copy it into a public repository.

Read `references/constitution-system.md` before initializing or validating a store.

## Workflow

1. Resolve the constitution home:
   - use `$AGENT_CONSTITUTION_HOME` when set;
   - otherwise use `~/.agent-constitution`.
2. If initialization is requested, run `scripts/init_constitution.py` from this skill.
3. Do not overwrite an existing `constitution.yaml` unless the user explicitly asks.
4. After initialization, report written paths and remind the user to keep live logs private.
5. For validation, run `scripts/validate_constitution.py <constitution-home>` and report the result.

## Commands

Initialize default location:

```bash
python3 <skill-dir>/scripts/init_constitution.py
```

Initialize a chosen location:

```bash
python3 <skill-dir>/scripts/init_constitution.py --home /path/to/.agent-constitution
```

Validate:

```bash
python3 <skill-dir>/scripts/validate_constitution.py /path/to/.agent-constitution
```

## Privacy Boundary

Never include private judgment logs, recommendation logs, API keys, account identifiers, private project paths, or live project history in a public skill package. Use the starter template only.

---
description: Add a new domain entity end-to-end (model → schema → service → router → authz → migration → frontend → tests → policy hooks)
argument-hint: <EntityName>
allowed-tools: Bash, Read, Write, Edit, Agent, Glob, Grep
---

# /add-entity

You are adding a new domain entity to the system. The entity name is `$ARGUMENTS`. Follow the canonical workflow in `@.agents/workflows/add-entity.md` exactly — the order matters because migrations and authz must be in place before the router goes live.

## Required reading

- `@.agents/rules/02-tech-stack-architecture.md` (folder responsibilities)
- `@.agents/rules/08-api-design-conventions.md` (REST conventions, response envelope, pagination)
- `@.agents/rules/09-testing-strategy.md` (what to test for new endpoints)
- `@.agents/rules/10-zero-hardcoded-business-logic.md` (no domain conditionals in services)
- `@.agents/rules/12-developer-guardrails.md` (entity lifecycle checklist)

## Execute the workflow

@.agents/workflows/add-entity.md

## Notes for Claude

- **Pillar check first.** Before writing code, confirm with the user which pillar this entity belongs to (Dashboard / Workbench / AI Engine). If it doesn't fit a pillar, document the exception in `decisionLog.md` (Rule 12 §2).
- **AuthZ is non-negotiable.** Add the entry to `app/authz.map.json` *before* the router goes live. After the router is written, invoke the `authz-auditor` subagent to verify.
- **Service layer must be thin.** No `if amount > X`, no `if status == Y`. Push every business decision through AI Policies (Rule 10).
- **Run the pre-commit checklist** (CLAUDE.md §6) before committing. Do not push.
- **Update the memory bank** at the end: `activeContext.md` and `progress.md`. If you made a non-obvious architectural decision, log it in `decisionLog.md`.

---
description: Initialize a new use case (Employee project) from the Supervity AI Command Center template
argument-hint: [optional use-case-name]
allowed-tools: Bash, Read, Write, Edit, Agent, Glob, Grep
---

# /start-new-usecase

You are bootstrapping a new Employee project from this template. Follow the canonical workflow in `@.agents/workflows/start-new-usecase.md` step by step. Do not skip steps. The use-case name (if provided) is `$ARGUMENTS`.

## Required reading before you begin

- `@.agents/rules/01-project-core.md` (project identity, the three pillars)
- `@.agents/rules/05-memory-bank-protocol.md` (memory bank file structure)
- `@.agents/rules/10-zero-hardcoded-business-logic.md` (the iron law)
- `@.agents/rules/11-data-ingestion-architecture.md` (ingestion adapter contract)
- `@.agents/rules/12-developer-guardrails.md` (entity lifecycle, authz, pillar check)

## Execute the workflow

@.agents/workflows/start-new-usecase.md

## Notes for Claude

- **Confirm before destructive demo removal.** Before deleting demo content (dashboard mocks, demo policies, brand page), list what you'll remove and ask the user to confirm. Log the removal in `docs/memory-bank/decisionLog.md`.
- **Ask the user the project-brief questions one at a time** (or in small batches) — don't dump the whole questionnaire. The answers shape every later step.
- **Never run `git push`.** Local commits only (Rule 04 §3).
- **Stop and prompt** if the user hasn't answered enough about data ingestion — you cannot scaffold the ingestion layer without knowing the source format.

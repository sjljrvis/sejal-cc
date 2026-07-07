---
description: Graduate a use case from POC data (CSV/JSON/PDF) to a production data source (SAP, ServiceNow, Workday, etc.)
argument-hint: <source-system>
allowed-tools: Bash, Read, Write, Edit, Agent, Glob, Grep
---

# /poc-to-production

You are transitioning the active use case from POC data to a production data source. Target system: `$ARGUMENTS`. Follow the canonical workflow in `@.agents/workflows/poc-to-production.md` step by step.

## Required reading

- `@.agents/rules/11-data-ingestion-architecture.md` (the adapter protocol — non-negotiable)
- `@.agents/rules/10-zero-hardcoded-business-logic.md` (policies, not code, drive decisions)
- `@.agents/rules/07-mcp-and-tooling.md` §3 (Cloud Run deploy considerations)
- `@.agents/rules/09-testing-strategy.md` §5 (mock external services in tests)

## Execute the workflow

@.agents/workflows/poc-to-production.md

## Critical guardrails for Claude

- **Never delete the POC adapter.** Mark it as POC and keep it for tests/demos (Step 11 of the workflow).
- **Run the policy regression (Step 8) before flipping `DATA_SOURCE`.** If outcomes diverge between POC and production data, **stop and surface the divergence to the user** rather than silently adjusting policies.
- **Production credentials never go in `.env.example`.** Only placeholders. Real secrets only in `.env` (which is gitignored).
- **Confirm before deploying.** If the user asks you to deploy after switching data sources, re-confirm the project ID, region, and target service. Never pick a project ID yourself (Rule 07 §3).
- **Do not run `git push`** — local commits only.

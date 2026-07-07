# Claude Code — Project Memory

> **You are working on the Supervity AI Command Center template.** This file is auto-loaded into context at the start of every Claude Code session. The rules below are the law of the codebase.
>
> **Single source of truth.** All rules live canonically in `.agents/rules/*.md`. Antigravity, Claude Code, Cursor, GitHub Copilot, Codex, Aider, and Cline all read the same content via tool-specific entry points. See `.agents/rules/README.md` for the full manifest.

## How to use this file

1. **Always-on rules** are embedded below via `@`-imports — they apply to every change you make in this repo.
2. **Conditional rules** live in `.agents/rules/` and are listed in §3 with descriptions of when to load them.
3. **Workflows** are exposed as slash commands under `.claude/commands/` (`/start-new-usecase`, `/add-entity`, `/poc-to-production`, `/memory-bank`).
4. **Specialized subagents** live in `.claude/agents/` — invoke them via the `Agent` tool when their description matches.

If a rule in this file ever conflicts with a rule in `.agents/rules/`, **the file in `.agents/rules/` wins** — it is canonical.

---

## 1. Always-on rules (read every session)

@.agents/rules/01-project-core.md
@.agents/rules/04-agent-execution-workflow.md
@.agents/rules/05-memory-bank-protocol.md
@.agents/rules/10-zero-hardcoded-business-logic.md
@.agents/rules/13-security-and-secrets.md

---

## 2. Session startup checklist (Memory Bank Protocol)

At the start of every new session, before doing feature work:

1. Verify `docs/memory-bank/` exists. If not, create it using the templates in `.agents/rules/05-memory-bank-protocol.md` §3.
2. Read `docs/memory-bank/projectbrief.md` — overall goal and use case.
3. Read `docs/memory-bank/activeContext.md` — what was being worked on last.
4. Read `docs/memory-bank/progress.md` — overall project status.

If any of those are empty or missing, fill them before continuing. Update them at the end of every significant task.

---

## 3. Conditional rules — read when the task touches the area

| Area | When to read | File |
|---|---|---|
| Tech stack / folder layout / picking a library | Adding a new service, choosing a library, restructuring folders | `@.agents/rules/02-tech-stack-architecture.md` |
| UI / styling / animation / brand | Building or modifying any visual element | `@.agents/rules/03-ui-animations-standard.md` |
| Gemini / AI services / policies | Implementing AI features, prompts, tool-calling, policy translation | `@.agents/rules/06-gemini-ai-patterns.md` |
| MCP / Make / env / deploy | Using MCP servers or running deploy/dev commands | `@.agents/rules/07-mcp-and-tooling.md` |
| API endpoints / schemas / pagination | Creating or modifying any API endpoint | `@.agents/rules/08-api-design-conventions.md` |
| Testing | Writing tests, fixtures, mocks | `@.agents/rules/09-testing-strategy.md` |
| Data ingestion adapters | Adding a new data source (CSV, SAP, ServiceNow, webhook) | `@.agents/rules/11-data-ingestion-architecture.md` |
| Authz / pillar fit / entity scaffolding / pre-commit | Adding endpoints, entities, or running the pre-commit self-check | `@.agents/rules/12-developer-guardrails.md` |
| Accessibility | Building any frontend UI component | `@.agents/rules/14-accessibility.md` |
| Logging / observability | Instrumenting AI calls, ingestion runs, background tasks, errors | `@.agents/rules/15-observability-and-logging.md` |

---

## 4. Slash commands (workflows)

Invoke with `/<name>` in the prompt. Each command is the structured workflow that lives canonically in `.agents/workflows/`.

- `/start-new-usecase` — Bootstrap a new Employee project from this template.
- `/add-entity` — Add a new domain entity end-to-end (model → schema → service → router → authz → migration → frontend → tests → policy hooks).
- `/poc-to-production` — Graduate from POC data (CSV/JSON) to a production source (SAP, ServiceNow, Workday).
- `/memory-bank` — Bootstrap or refresh `docs/memory-bank/`.

---

## 5. Subagents

Use the `Agent` tool with the matching `subagent_type` when the work fits one of these specialists. They have isolated context windows so they don't pollute the main thread.

- **`ui-design-reviewer`** — Reviews UI diffs against `docs/brand-identity.md` and Rule 03 (and now Rule 14 for a11y). Run before committing UI changes.
- **`policy-conflict-checker`** — Wraps the RuleArchitect flow: every new AI Policy must go through it for conflict / override / clarification analysis (Rule 06 §8).
- **`authz-auditor`** — Walks new router endpoints and confirms each has a matching entry in `app/authz.map.json` (Rule 12 §3).

---

## 6. Pre-commit self-check (mandatory)

Before any `git commit`:

- [ ] Frontend: `cd frontend && npm run lint && npm run build` passes
- [ ] Backend: `make lint && make test-be` passes
- [ ] No hardcoded business logic (Rule 10)
- [ ] Every new endpoint has an authz rule in `authz.map.json` (Rule 12 §3)
- [ ] UI uses semantic brand tokens **and** passes the a11y bar (Rules 03 + 14)
- [ ] No `console.log`, `print()`, unused imports, dead code (Rule 04 §4)
- [ ] No secrets in tracked code, no PII in logs (Rule 13)
- [ ] Tests exist for new endpoints (Rule 09)
- [ ] Logging uses structured events with masked sensitive fields (Rule 15)
- [ ] Memory Bank updated if the change is significant (Rule 05 §4)

Never run `git push`. That's a human decision (Rule 04 §3).

---

## 7. Environment quick reference

- Start dev: `make up` · Stop: `make down` · Logs: `make logs-be` / `make logs-fe`
- Migrations: `make migrate-create MSG='...'` → `make migrate-up`
- Reset DB: `make reset-db`
- Lint/format: `make lint` / `make format`
- Tests: `make test-be`
- Sync rules to Cursor mirror after editing canonical: `make sync-rules`
- Backend hot-reloads in `APP_ENV=development`. Frontend needs `docker compose build frontend` if `FRONTEND_TARGET=prod`.

Full env var list is in `.env.example`.

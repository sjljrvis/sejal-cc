# AGENTS.md — Supervity AI Command Center

This repo is shared across multiple AI coding agents. **All agents follow the same canonical rules.** They live once in `.agents/rules/` and `.agents/workflows/`. Each agent has a thin entry-point file that points back to that single source.

## Auto-loading by agent (no per-developer setup needed)

| Agent | Entry file (auto-loaded) | What it does |
|---|---|---|
| **Antigravity** | `.agents/rules/*.md` (native) | Reads files with `trigger: always_on`; conditionally loads `trigger: model_decision` files when the description matches |
| **Claude Code** | `CLAUDE.md` (project root) | `@`-imports the always-on rules and lists conditional rules with descriptions. Slash commands in `.claude/commands/`, subagents in `.claude/agents/` |
| **Cursor** | `.cursor/rules/*.mdc` | Mirrored from `.agents/rules/` via `scripts/sync-rules.sh`. Cursor frontmatter (`alwaysApply` / `globs` / `description`) drives auto-loading |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Pointer to this directory |
| **Codex / Aider / Cline / others** | `AGENTS.md` (this file) | Tool-agnostic pointer |

If you're an agent reading this for the first time, this is everything you need. Open `.agents/rules/01-project-core.md`, `.agents/rules/05-memory-bank-protocol.md`, then come back here.

## Source of truth

| What | Where |
|---|---|
| Rules (always-on + conditional) | `.agents/rules/*.md` |
| Rule manifest | `.agents/rules/README.md` |
| Workflows (multi-step procedures) | `.agents/workflows/*.md` |
| Memory bank (project state) | `docs/memory-bank/` |
| Brand & design system | `docs/brand-identity.md`, `docs/design-system-template.md` |
| Use-case documentation | `docs/{use-case}.md` |
| Architecture overview | `docs/cc-playbook.md` |
| Audit logging | `docs/Audit System Guide.md` |
| Auth | `docs/Keycloak Developer Guide.md` |

## Always-on rules (every agent reads these every session)

1. `.agents/rules/01-project-core.md` — project identity, three pillars, brand basics, internal-tool boundary
2. `.agents/rules/04-agent-execution-workflow.md` — execution discipline, pre-commit checks, no `git push`
3. `.agents/rules/05-memory-bank-protocol.md` — read `docs/memory-bank/` at session start
4. `.agents/rules/10-zero-hardcoded-business-logic.md` — the iron law: business decisions go through AI Policies
5. `.agents/rules/13-security-and-secrets.md` — secrets hygiene, OWASP awareness, AI-specific threats

## Conditional rules (read when the task touches the area)

| Area | File |
|---|---|
| Tech stack / folder layout | `.agents/rules/02-tech-stack-architecture.md` |
| UI / styling / animation | `.agents/rules/03-ui-animations-standard.md` |
| Gemini / AI services / policies | `.agents/rules/06-gemini-ai-patterns.md` |
| MCP / Make / env / deploy | `.agents/rules/07-mcp-and-tooling.md` |
| API endpoints / schemas | `.agents/rules/08-api-design-conventions.md` |
| Testing | `.agents/rules/09-testing-strategy.md` |
| Data ingestion adapters | `.agents/rules/11-data-ingestion-architecture.md` |
| Authz / pillar fit / pre-commit | `.agents/rules/12-developer-guardrails.md` |
| Accessibility | `.agents/rules/14-accessibility.md` |
| Logging / observability | `.agents/rules/15-observability-and-logging.md` |

## Workflows (multi-step procedures)

- `.agents/workflows/start-new-usecase.md` — bootstrap a new Employee project
- `.agents/workflows/add-entity.md` — add a new domain entity end-to-end
- `.agents/workflows/poc-to-production.md` — graduate from POC data to a production source

## Hard rules every agent must follow

1. **Memory bank first.** At session start, verify `docs/memory-bank/` exists and read `projectbrief.md` + `activeContext.md` + `progress.md`. Bootstrap if missing (Rule 05).
2. **No hardcoded business logic.** All domain decisions go through AI Policies (Rule 10).
3. **Authz is mandatory.** Every new endpoint needs an entry in `app/authz.map.json` before commit (Rule 12 §3).
4. **Pre-commit checks are not optional.** Frontend `npm run lint && npm run build`. Backend `make lint && make test-be` (Rule 04 §2).
5. **Never `git push`.** Pushing is a human decision (Rule 04 §3).
6. **Use the design system.** No raw hex, no arbitrary pixel sizes, no marketing copy (Rule 03). Internal command center, not a public site (Rule 01 §3).
7. **Accessibility is the bar.** Every UI component meets WCAG 2.2 AA — keyboard nav, semantic HTML, ARIA, contrast (Rule 14).
8. **No secrets in tracked code.** No PII in logs unmasked (Rules 13 + 15).
9. **Update the memory bank** at the end of any significant task (`activeContext.md`, `progress.md`, and `decisionLog.md` for architectural decisions).

## Maintenance

To edit a rule: change the canonical file in `.agents/rules/`, then run `make sync-rules` (or `bash scripts/sync-rules.sh`) to regenerate the Cursor mirror. `CLAUDE.md`, this file, and `.github/copilot-instructions.md` reference the canonical files so they don't need a sync step.

Adding a new rule? See `.agents/rules/README.md` for the procedure.

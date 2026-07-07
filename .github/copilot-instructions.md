# GitHub Copilot — Project Instructions

This repository uses a tool-agnostic ruleset that lives in `.agents/rules/`. Copilot, Cursor, Claude Code, Antigravity, and other agents all share the same rules — only the entry-point file differs.

## What to read first

When you start a session in this repo, read these files in order:

1. **`.agents/rules/README.md`** — full manifest of every rule.
2. **Always-on rules** — load these before doing any work:
   - `.agents/rules/01-project-core.md`
   - `.agents/rules/04-agent-execution-workflow.md`
   - `.agents/rules/05-memory-bank-protocol.md`
   - `.agents/rules/10-zero-hardcoded-business-logic.md`
   - `.agents/rules/13-security-and-secrets.md`
3. **Memory bank** — read these on every session:
   - `docs/memory-bank/projectbrief.md`
   - `docs/memory-bank/activeContext.md`
   - `docs/memory-bank/progress.md`

## Conditional rules — read when the task touches the area

| Area | File |
|---|---|
| Tech stack / folder layout | `.agents/rules/02-tech-stack-architecture.md` |
| UI / styling / animation | `.agents/rules/03-ui-animations-standard.md` |
| AI services / Gemini / policies | `.agents/rules/06-gemini-ai-patterns.md` |
| MCP / Make / env / deploy | `.agents/rules/07-mcp-and-tooling.md` |
| API endpoints / schemas | `.agents/rules/08-api-design-conventions.md` |
| Testing | `.agents/rules/09-testing-strategy.md` |
| Data ingestion | `.agents/rules/11-data-ingestion-architecture.md` |
| Authz / pre-commit / pillar fit | `.agents/rules/12-developer-guardrails.md` |
| Accessibility | `.agents/rules/14-accessibility.md` |
| Logging / observability | `.agents/rules/15-observability-and-logging.md` |

## Hard rules

- **Memory bank first.** Verify `docs/memory-bank/` exists; bootstrap if missing (template in rule 05).
- **No hardcoded business logic.** Every domain decision goes through AI Policies (rule 10).
- **Authz is mandatory.** Every new endpoint needs an entry in `app/authz.map.json` before commit (rule 12 §3).
- **Pre-commit checks are not optional.** Frontend `npm run lint && npm run build`. Backend `make lint && make test-be`.
- **Never `git push`.** Pushing is a human decision.
- **No secrets in tracked code** (rule 13).
- **Update the memory bank** at the end of any significant task.

For full details on any rule, open the file in `.agents/rules/`. For multi-step procedures (start a use case, add an entity, POC→production), see `.agents/workflows/`.

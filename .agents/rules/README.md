# `.agents/rules/` — Canonical Rules

This directory is the **single source of truth** for the rules every AI coding agent in this repo must follow. Antigravity reads these files directly. Claude Code, Cursor, GitHub Copilot, Codex, Aider, and Cline all read mirrored or pointer files that ultimately defer to this directory.

## How to read this directory

Every file is Markdown with YAML frontmatter:

```yaml
---
trigger: always_on              # or `model_decision`
description: <when to load>     # required when trigger is model_decision
---
```

- **`trigger: always_on`** — load every session, no matter the task.
- **`trigger: model_decision`** — load when the task description matches the rule's `description`.

If you're an agent and you see this file: the rules numbered 01, 04, 05, 10, 13 are mandatory reads at session start. The rest are conditional — load them when relevant.

## Manifest

| # | Title | Trigger | Owns |
|---|---|---|---|
| 01 | Project Core | always_on | Identity, three pillars, brand basics |
| 02 | Tech Stack & Architecture | model_decision | Backend/frontend stack, folder layout |
| 03 | UI & Animations Standard | model_decision | Brand tokens, components, animations |
| 04 | Agent Execution Workflow | always_on | Step-by-step strategy, pre-commit, git discipline |
| 05 | Memory Bank Protocol | always_on | Session context, `docs/memory-bank/` files |
| 06 | Gemini AI Patterns | model_decision | AI abstraction, prompts, tool calling, policies |
| 07 | MCP & Tooling | model_decision | MCP servers, Make commands, env vars |
| 08 | API Design Conventions | model_decision | REST patterns, response envelopes, status codes |
| 09 | Testing Strategy | model_decision | What/where/how to test |
| 10 | Zero Hardcoded Business Logic | always_on | The Iron Law: decisions go through AI Policies |
| 11 | Data Ingestion Architecture | model_decision | Adapter protocol, POC vs production sources |
| 12 | Developer Guardrails | model_decision | Pillar check, authz, anti-patterns, entity lifecycle |
| 13 | Security & Secrets | always_on | Secrets handling, OWASP awareness, AI-specific threats |
| 14 | Accessibility | model_decision | WCAG 2.2 AA bar for every UI component |
| 15 | Observability & Logging | model_decision | Log levels, structured events, masking, audit boundary |

## Where each agent reads from

| Agent | Reads | Notes |
|---|---|---|
| **Antigravity** | `.agents/rules/*.md` (this directory) | Native — frontmatter is in Antigravity's format |
| **Claude Code** | `CLAUDE.md` (root) | `@`-imports the always-on rules from this directory |
| **Cursor** | `.cursor/rules/*.mdc` | Mirrored via `scripts/sync-rules.sh`. Each MDC has Cursor frontmatter (`alwaysApply` / `globs` / `description`) |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Pointer file that lists this directory |
| **Codex / Aider / Cline / others** | `AGENTS.md` (root) | Tool-agnostic pointer to this directory |

## Maintenance — Editing a Rule

**Always edit the canonical file in `.agents/rules/` first.** Then regenerate the Cursor mirror:

```bash
make sync-rules     # preferred — wraps the script
# or:
bash scripts/sync-rules.sh
```

That script:
1. Reads each `.agents/rules/*.md`.
2. Strips the Antigravity frontmatter.
3. Adds the matching Cursor frontmatter from the mapping table inside the script.
4. Writes the result to `.cursor/rules/*.mdc`.

`CLAUDE.md`, `AGENTS.md`, and `.github/copilot-instructions.md` reference the canonical files via path or `@`-import — they don't duplicate content, so they don't need a sync step.

## Adding a new rule

1. Create `.agents/rules/NN-title.md` with proper frontmatter.
2. Add a row to the manifest above.
3. Add an entry to the Cursor mapping table in `scripts/sync-rules.sh`.
4. Run `make sync-rules`.
5. If the rule is `always_on`, add an `@`-import to `CLAUDE.md` §1 and a row to `AGENTS.md`'s always-on list.
6. Commit everything in one commit with a `docs:` prefix.

## Removing a rule

1. Delete `.agents/rules/NN-title.md`.
2. Delete `.cursor/rules/NN-title.mdc`.
3. Remove the row from this manifest, from `CLAUDE.md` (if always-on), from `AGENTS.md`, and from the mapping in `scripts/sync-rules.sh`.
4. Commit.

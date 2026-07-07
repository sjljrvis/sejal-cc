---
description: Bootstrap or refresh the docs/memory-bank/ files (projectbrief, activeContext, progress, decisionLog)
allowed-tools: Bash, Read, Write, Edit
---

# /memory-bank

Run the Memory Bank protocol. Use this at the start of a new session, after a major task, or whenever the memory bank looks stale.

## Behavior

1. **Bootstrap if missing.** If `docs/memory-bank/` doesn't exist, create it and scaffold the four files using the templates in `@.agents/rules/05-memory-bank-protocol.md` §3:
   - `projectbrief.md`
   - `activeContext.md`
   - `progress.md`
   - `decisionLog.md`

2. **Read & report.** If the directory exists, read all four files and give the user a 5–10 line summary:
   - The use case (from `projectbrief.md`)
   - What was being worked on last (from `activeContext.md`)
   - Recent progress and what's next (from `progress.md`)
   - Any architectural decisions that bound the current work (from `decisionLog.md`)

3. **Refresh.** Ask the user whether anything in the memory bank is out of date. If `activeContext.md` references work that's already merged, propose updates and apply them after confirmation.

## Notes

- This file is canonical: `@.agents/rules/05-memory-bank-protocol.md`. If the protocol there changes, this command follows it.
- Don't fabricate content. If a section is empty, ask the user to fill it in rather than guessing.
- Commit memory-bank updates with the `docs:` prefix.

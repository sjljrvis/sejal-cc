---
trigger: always_on
---

# 1. The "Memory Bank" Pattern (CRITICAL)
You are an autonomous AI spanning multiple sessions. You suffer from amnesia between sessions. To maintain context, you MUST utilize the Memory Bank located in `docs/memory-bank/`.

**If the `docs/memory-bank/` folder does not exist, you MUST create it and bootstrap the required files before doing anything else.** This is your first action in any new project.

# 2. Session Startup Protocol (EVERY SESSION)
At the **beginning of every new chat session**, you MUST:
1. Check if `docs/memory-bank/` exists. If not, create it with the files described in Section 3.
2. Read `docs/memory-bank/projectbrief.md` (to remember the overall goal and use case).
3. Read `docs/memory-bank/activeContext.md` (to remember what was being worked on last).
4. Read `docs/memory-bank/progress.md` (to understand overall project status).

If any of these files are empty or missing, prompt yourself to fill them before proceeding with feature work.

# 3. Memory Bank File Structure
When bootstrapping, create these files inside `docs/memory-bank/`:

### `projectbrief.md` — The Use Case Definition
This is the most important file. It defines WHAT this Employee is being built for.
```markdown
# Project Brief: [Employee Name / Use Case]

## Business Context
- What problem does this solve?
- Who are the stakeholders / end users?
- What business process does this automate or augment?

## What We're Building
- **Dashboard (Eyes):** What insights and KPIs will be shown?
- **Workbench (Hands):** What records/exceptions will operators handle?
- **AI Engine (Brain):** What rules/policies will the AI follow?

## Data Model (High-Level)
- What are the core entities? (e.g., Tickets, Orders, Claims)
- What data does the AI ingest? What does it output?
- What feedback loops exist?

## Integrations
- External systems, APIs, data sources

## Success Criteria
- How do we know this is working?
```

### `activeContext.md` — What's Happening Right Now
```markdown
# Active Context

## Currently Working On
[What feature/task is in progress]

## Current State
[What is built, what is running, what is broken]

## Immediate Next Steps
[1-3 concrete next actions]

## Blockers
[Anything preventing progress]

## Recent Changes
[Last 3-5 significant changes made]
```

### `progress.md` — What's Done
```markdown
# Progress Log

## Completed
- [x] Item with date

## In Progress
- [/] Item

## Planned
- [ ] Item
```

### `decisionLog.md` — Why We Did What We Did
```markdown
# Decision Log

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
```

# 4. Writing Context (End of Task / Session)
When you complete a major task, feature, or refactor, you MUST update the Memory Bank before concluding:
1. Update `docs/memory-bank/progress.md` with what was just completed.
2. Update `docs/memory-bank/activeContext.md` with the current state and what the immediate next steps are.
3. If you made a major architectural decision (e.g., choosing a new library, changing folder structure, picking a data model), log it in `docs/memory-bank/decisionLog.md`.

# 5. New Use Case Onboarding (Starting a Real Project)
When transitioning from the template to a real use case, follow this protocol:

### Step 1: Create the Project Brief
Fill out `docs/memory-bank/projectbrief.md` with the specific use case details. This is the **first thing** you do before writing any code.

### Step 2: Identify & Remove Demo Content
The template ships with demo/placeholder content. Before building real features:
- **Dashboard (`/` page):** Replace mock stats and placeholder charts with real data endpoints.
- **Workbench (`/workbench`):** Replace placeholder UI with the actual AI workflow for this use case.
- **Settings (`/settings`):** Implement real configuration options.
- **Demo Policies:** Remove demo AI policies and replace with domain-specific rules.
- **Brand page (`/brand`):** Remove from sidebar navigation (internal reference only).
- **Log every removal** in `docs/memory-bank/decisionLog.md` with rationale for what was kept vs removed.

### Step 3: Create Use Case Documentation
Create a dedicated `docs/{use-case-name}.md` file documenting:
- Domain-specific data flow (Ingest → Enrich → Analyze → Act → Learn)
- AI integration points (what the AI does at each stage)
- API contract (key endpoints)
- Entity relationships

### Step 4: Update Agent Rules (if needed)
If the use case introduces domain-specific conventions (e.g., specific naming patterns, unique validation rules, new service integrations), update the relevant rule files in `.agents/rules/`.

# 6. Key Project Documentation
Before building features, always check whether these docs have relevant context:
- `docs/brand-identity.md` — Full Ampersand design token map, color palette, logo assets.
- `docs/design-system-template.md` — UI component patterns, spacing, layout templates.
- `docs/cc-playbook.md` — Command Center philosophy, AI-First design, 3-pillar architecture.
- `docs/Audit System Guide.md` — Audit logging patterns, middleware config, API endpoints.
- `docs/Keycloak Developer Guide.md` — Authorization engine, RBAC/ABAC rules, policy language.

# 7. The "Boy Scout" Rule (Self-Evolving Codebase)
Whenever you touch existing code, look for opportunities to improve it safely:
- Extract hardcoded strings or magic numbers.
- Improve component or function readability.
- If you introduce a new system (e.g., data pipeline, new AI service, integration module), create a dedicated documentation file for it in `/docs/`.
---
description: How to initialize a new use case from the Supervity AI Command Center template
---

# Start New Use Case

Follow these steps in order when beginning a new use case / Employee project from the template.

## Step 1: Bootstrap Memory Bank
// turbo
1. Check if `docs/memory-bank/` exists. If not, create it:
```bash
mkdir -p docs/memory-bank
```

2. Create the four required files:
   - `docs/memory-bank/projectbrief.md`
   - `docs/memory-bank/activeContext.md`
   - `docs/memory-bank/progress.md`
   - `docs/memory-bank/decisionLog.md`

Use the templates from `.agents/rules/05-memory-bank-protocol.md` Section 3.

## Step 2: Fill Out the Project Brief
3. Ask the user for:
   - What business problem are we solving?
   - Who are the end users?
   - What does the Dashboard show? (KPIs, insights)
   - What does the Workbench handle? (records, exceptions, workflows)
   - What AI capabilities are needed? (classification, extraction, recommendations)
   - What data sources / integrations exist?

4. Write the answers into `docs/memory-bank/projectbrief.md`.

## Step 3: Create Use Case Documentation
5. Create `docs/{use-case-name}.md` documenting:
   - The operational loop: Ingest → Enrich → Analyze → Act → Learn
   - Data model (core entities and relationships)
   - AI integration points
   - API contracts (planned endpoints)

## Step 3.5: Set Up Ingestion Layer
6. Create the ingestion infrastructure:
```bash
mkdir -p app/services/ingestion/adapters
```
7. Define the `IngestionAdapter` protocol in `app/services/ingestion/__init__.py` (see Rule 11).
8. Create the initial POC adapter (likely `CSVAdapter` or `JSONAdapter`) for the use case's data format.
9. Create `field_mapping.json` mapping source field names to internal schema fields.
10. Ensure ingestion calls the internal service layer — never writes to DB directly.

## Step 4: Identify & Remove Demo Content
11. Review and list all demo/placeholder content that needs replacement:
   - Dashboard (`/` page) — mock stats and charts
   - Workbench (`/workbench`) — placeholder UI
   - Settings (`/settings`) — placeholder config
   - Demo AI Policies — sample rules
   - Brand page (`/brand`) — remove from sidebar nav

12. Log removals in `docs/memory-bank/decisionLog.md` with rationale for what was kept vs removed.

## Step 4.5: Define Policy Hooks
13. For each entity in the data model, define where AI Policies should evaluate:
   - **On ingestion:** Validate and classify incoming data
   - **On status change:** Approval/rejection/escalation rules
   - **On assignment:** Route to team/person
   - **On threshold:** Check limits, quotas, budgets
   - **On schedule:** SLA checks, aging analysis
14. Document these hooks in `docs/{use-case-name}.md`.

## Step 5: Set Up the Data Model
15. Define SQLAlchemy models in `/app/models/` for the use case entities.
16. Create Pydantic schemas in `/app/schemas/`.
17. Generate Alembic migration:
```bash
make migrate-create MSG='initial_{use_case}_models'
```
18. Apply migration:
```bash
make migrate-up
```

## Step 6: Scaffold the API
19. Create router(s) in `/app/routers/` following `08-api-design-conventions.md`.
20. Create service(s) in `/app/services/` for business logic — **NO domain conditionals** (Rule 10).
21. If AI is involved, add capabilities in `/app/services/ai/`.
22. **MANDATORY:** Update `app/authz.map.json` with authorization rules for ALL new endpoints (Rule 12).

## Step 7: Scaffold the Frontend
23. Create page(s) in `/frontend/src/app/` for the use case.
24. Update sidebar navigation in `/frontend/src/components/layout/Sidebar.tsx`.
25. Create domain components in `/frontend/src/components/{use-case}/`.
26. **Reference `docs/brand-identity.md`** for all design tokens (Rule 03, Section 9).

## Step 7.5: Wire Up Feedback Loop
27. In Workbench components, add a "Teach AI" button pattern for human feedback.
28. This button should capture the human's correction and create/refine an AI Policy.
29. Example flow: Human overrides AI decision → clicks "Teach AI" → writes rule in natural language → policy is created via `/ai/policies`.

## Step 8: Verify & Commit
30. Run pre-commit checks:
```bash
cd frontend && npm run lint && npm run build
```
```bash
make test-be
```

31. Commit the scaffold:
```bash
git add -A && git commit -m "feat: scaffold {use-case-name} use case"
```

## Step 9: Update Active Context
32. Update `docs/memory-bank/activeContext.md` with:
    - What was set up
    - Current state (scaffold complete, ready for feature work)
    - Immediate next steps

33. Update `docs/memory-bank/progress.md` marking the scaffold as complete.

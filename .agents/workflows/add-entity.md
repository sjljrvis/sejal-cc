---
description: How to add a new domain entity (model, schema, service, router, authz, migration, frontend, tests, policies)
---

# Add Entity Workflow

Use this workflow when adding a new domain entity to the system (e.g., Ticket, Invoice, Order, Claim).

## Prerequisites
- Memory Bank is set up with project brief filled
- Use case documentation exists in `docs/`
- You know which pillar this entity belongs to (Dashboard / Workbench / AI Engine)

## Steps

### 1. Create the SQLAlchemy Model
Create `app/models/{entity}.py`:
- Define all columns with proper types and constraints
- Include `id`, `created_at`, `updated_at` as minimum fields
- Add relationships if needed
- Export in `app/models/__init__.py`

// turbo
### 2. Create Pydantic Schemas
Create `app/schemas/{entity}.py` with these schemas:
- `{Entity}Base` — shared fields
- `{Entity}Create` — fields for creation (exclude auto-generated like id, timestamps)
- `{Entity}Update` — all fields optional for partial updates
- `{Entity}Response` — full response including id, timestamps
- `{Entity}ListResponse` — paginated list wrapper (items + total + pagination metadata)

### 3. Create the Service Layer
Create `app/services/{entity}.py`:
- CRUD operations only: `create()`, `get()`, `list()`, `update()`, `delete()`
- **NO business logic** — no if/else domain decisions (Rule 10)
- Policy evaluation calls go here (call `rule_engine.apply_policies()`)
- Import and use the model and schemas

### 4. Create the Router
Create `app/routers/{entity}.py`:
- Thin layer — delegates entirely to the service
- Standard REST endpoints: `POST /`, `GET /`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`
- Follow API conventions from Rule 08 (response envelopes, status codes, pagination)
- Add `Depends(get_current_user)` and `Depends(get_db)` to all endpoints
- Register router in `app/main.py`

### 5. Add AuthZ Rules (MANDATORY)
Add rules to `app/authz.map.json` for ALL new endpoints:
```json
"/api/{entities}.*": {
    "description": "{Entity} operations - requires approved user",
    "ANY": ["admin", "user"]
}
```
Adjust roles as needed. **Do NOT skip this step.**

// turbo
### 6. Generate Database Migration
```bash
make migrate-create MSG='add_{entity}_table'
```
Review the generated file in `alembic/versions/`, then apply:
```bash
make migrate-up
```
Verify with:
```bash
make migrate-history
```

### 7. Add Ingestion Support
If this entity receives data from external sources:
- Add a `parse_{entity}()` method to the relevant ingestion adapter
- Define field mapping for this entity's source fields → internal schema
- Test ingestion with sample data (CSV row → database record)

### 8. Create Frontend Page
- Create page at `frontend/src/app/{entity}/page.tsx`
- Create components in `frontend/src/components/{entity}/`
- **Reference `docs/brand-identity.md`** for design tokens
- Use `shadcn/ui` primitives before custom components
- Include loading states (shimmer), empty states, and error handling
- Add API client hooks in `frontend/src/hooks/` or `frontend/src/lib/api/`

### 9. Add Sidebar Navigation
Update `frontend/src/components/layout/Sidebar.tsx`:
- Add nav entry with appropriate `lucide-react` icon
- Place under the correct pillar section (Dashboard / Workbench / AI Engine)

### 10. Write Tests
Create `tests/test_{entity}.py`:
- At least 2 tests per endpoint (success case + error case)
- Test CRUD operations
- Test authorization (accessing without proper role)
- Mock the AI service if policies are evaluated
- Follow patterns from Rule 09

### 11. Define Policy Hooks
Document in `docs/{use-case}.md` — where should AI Policies evaluate this entity?
- **On ingestion:** Validate/classify when data enters
- **On status change:** Approval/rejection/escalation
- **On assignment:** Route to team/person
- **On threshold:** Check limits, quotas, budgets
- **On schedule:** SLA checks, aging analysis

Wire up policy evaluation in the service layer where applicable.

### 12. Update Memory Bank
- Update `docs/memory-bank/activeContext.md` with current state
- Update `docs/memory-bank/progress.md` marking this entity as complete
- If any architectural decisions were made, log in `docs/memory-bank/decisionLog.md`

## Pre-Commit Checklist
Before committing, verify:
- [ ] No hardcoded business logic in service or router
- [ ] AuthZ rule exists in `authz.map.json`
- [ ] UI follows brand-identity.md
- [ ] No dead code, unused imports, console.log
- [ ] Tests pass
- [ ] Migration applied and verified
- [ ] Memory Bank updated

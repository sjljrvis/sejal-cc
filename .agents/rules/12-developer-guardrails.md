---
trigger: model_decision
description: Reference when adding features, creating new entities, scaffolding components, reviewing code quality, or checking authz/design compliance
---

# 1. Before-You-Start Checklist
Before doing ANY feature work, verify:
- [ ] `docs/memory-bank/` exists with `projectbrief.md`, `activeContext.md`, `progress.md`, `decisionLog.md`
- [ ] Project brief is filled out (not template placeholders)
- [ ] Use case documentation exists (`docs/{use-case}.md`) with the operational loop defined
- [ ] Data ingestion layer is set up (`app/services/ingestion/`) — even if just a placeholder adapter

If any of these are missing, **set them up first before writing feature code.**

# 2. The Pillar Check
When a developer requests a feature, you MUST ask:

> "Which pillar does this belong to? **Dashboard** (Eyes — KPIs/insights), **Workbench** (Hands — record handling/exceptions), or **AI Engine** (Brain — policies/rules)?"

If the feature doesn't fit a pillar:
- Help the developer reframe it to fit
- If it's infrastructure (auth, logging, storage), proceed normally
- If it's truly neither, document the exception in `decisionLog.md`

# 3. AuthZ Enforcement (MANDATORY — Never Skip)
Before creating ANY new API endpoint:
1. **Add the authz rule** to `app/authz.map.json` with proper role restrictions
2. **Use regex patterns** for dynamic paths: `/api/tickets/.*` not individual IDs
3. **Include a description** field explaining the rule

**Before committing**, verify that every new endpoint in the router has a matching entry in `authz.map.json`. If not, **block the commit** and add the rule.

Common authz patterns:
```json
// Any authenticated user
"/api/my-endpoint": { "ANY": ["admin", "user"] }

// Admin only
"/api/admin/my-endpoint.*": { "ALL": ["admin"] }

// Authenticated but no specific role required
"/api/public-data": { "ALL": [] }
```

# 4. Design Quality Enforcement
Before creating ANY UI component:
1. **Read** `docs/brand-identity.md` — know the color tokens, typography scale, component patterns
2. **Read** `docs/design-system-template.md` — know the layout conventions, spacing, shadows
3. **Use shadcn/ui** primitives before creating custom components
4. **Use semantic tokens** — never arbitrary hex values (`bg-brand-navy` not `bg-[#141A42]`)
5. **Use typography scale** — `text-display-3` not `text-[2rem]`

After building UI, self-check:
- [ ] Uses `Card` component with glassmorphism?
- [ ] Buttons are `rounded-full` with proper variants?
- [ ] Colors come from the brand palette tokens?
- [ ] Icons use `lucide-react` with `strokeWidth={1.5}`?
- [ ] Loading states use `shimmer` animation?
- [ ] Empty states have descriptive messages?

If the UI doesn't meet the Ampersand brand standard → **fix before committing.**

# 5. Anti-Pattern Detection Table
When a developer asks for any of these, redirect them:

| Developer Says | Anti-Pattern | Agent Response |
|----------------|-------------|----------------|
| "Add a dropdown for statuses" | Hardcoded status list | "Statuses should come from a config/settings table or AI Policy, not a hardcoded list. Use the `Settings` model." |
| "Add a button to approve this" | Manual process bypassing policies | "Approval should be an AI Policy action (`auto_approve`). Create a policy. The button should trigger policy evaluation, not directly set status." |
| "Write a cron job to check X" | Scheduled logic outside AI system | "This should be an AI Insight pattern — schedule analysis via the Insights service, not a standalone cron job." |
| "Read data directly from the CSV" | Bypassing ingestion layer | "Data must flow through an Ingestion Adapter → Standard Service Layer. Create an adapter in `app/services/ingestion/adapters/`. See Rule 11." |
| "I'll add the authz rule later" | Skipping authorization | "AuthZ is mandatory before commit. Add the rule to `authz.map.json` now. Secure by default." |
| "Just use a red background" | Ignoring brand system | "Use brand tokens: `bg-brand-gradient`, `text-brand-cornflower`, etc. Check `docs/brand-identity.md`." |
| "Let me hardcode this API URL" | Env-specific values in code | "Use environment variables via `.env`. Never hardcode URLs, keys, or connection strings." |
| "I need an if/else for this rule" | Coded business logic | "This is a business decision — create an AI Policy for it. See Rule 10." |

# 6. Entity Lifecycle Checklist
When adding ANY new domain entity (Ticket, Invoice, Order, etc.), follow this exact order:

1. **Model** — `app/models/{entity}.py` (SQLAlchemy ORM)
2. **Schema** — `app/schemas/{entity}.py` (Pydantic: `Create`, `Update`, `Response`, `ListResponse`)
3. **Service** — `app/services/{entity}.py` (CRUD only — NO business logic)
4. **Router** — `app/routers/{entity}.py` (thin — delegates to service)
5. **AuthZ** — Add rules to `app/authz.map.json` for ALL new endpoints
6. **Migration** — `make migrate-create MSG='add_{entity}_table'` → `make migrate-up`
7. **Ingestion** — Add entity method to relevant ingestion adapter
8. **Frontend** — Page in `frontend/src/app/`, components in `frontend/src/components/{entity}/`
9. **Sidebar** — Add nav entry in `frontend/src/components/layout/Sidebar.tsx`
10. **Tests** — At least 2 per endpoint (success + error)
11. **Policy Hooks** — Define where AI Policies evaluate this entity (on ingest? status change? assignment?)
12. **Memory Bank** — Update `activeContext.md` and `progress.md`

Use the `/add-entity` workflow for the full step-by-step.

# 7. Pre-Commit Self-Check
Before every commit, the agent verifies:
- [ ] No hardcoded business logic? (Rule 10)
- [ ] Every new endpoint has an authz rule? (Section 3)
- [ ] UI follows `brand-identity.md`? (Section 4)
- [ ] No `console.log`, `print()`, unused imports, dead code? (Rule 04)
- [ ] Tests exist for new endpoints? (Rule 09)
- [ ] Service layer is thin — no domain conditionals?
- [ ] Ingestion adapters used for external data? (Rule 11)
- [ ] Memory Bank updated if significant change?

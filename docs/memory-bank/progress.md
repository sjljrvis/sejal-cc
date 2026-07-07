# Progress Log

## Completed
- [x] Pin cryptography>=44,<47 to dodge v48 SIGILL on Apple Silicon Docker — 2026-05-08
- [x] Bump Next.js 15.5.11 → 15.5.18 (security fixes + fix @next/swc lockfile drift) — 2026-05-08
- [x] Migrated AI stack to Gemini 3 (model, thinking_level, thought_signatures, SDK floor) — 2026-05-07
- [x] Removed hardcoded API key from scripts/test_ai.py; tightened Rule 13 — 2026-05-07
- [x] Refactored RuleArchitect/PromptOptimizer to subclass GeminiService (single source of truth) — 2026-05-07
- [x] Keycloak Admin pagination & search (server-side) — 2026-05-05
- [x] AI Policies deep dive & gap analysis — 2026-05-05
- [x] AI Policies DB persistence (SQLAlchemy model + Alembic migration) — 2026-05-05
- [x] PolicyCRUD service for database operations — 2026-05-05
- [x] Rewrite AI router from in-memory dict to DB — 2026-05-05
- [x] Add conflict detection to policy creation (backend + frontend) — 2026-05-05
- [x] Fix async Gemini calls in RuleArchitect/PromptOptimizer — 2026-05-05
- [x] Add re-analysis on policy update when natural_language changes — 2026-05-05
- [x] Wire Structured Builder save button — 2026-05-05
- [x] Add policy_scope field (base/instruction/custom) to schema/model/UI — 2026-05-05
- [x] Add source field for demo/user data separation — 2026-05-05
- [x] AI Insights DB persistence (SQLAlchemy model + Alembic migration) — 2026-05-05
- [x] InsightCRUD service for database operations — 2026-05-05
- [x] Rewrite Insights router from in-memory cache to DB — 2026-05-05
- [x] Add dismiss/action persistence endpoints — 2026-05-05
- [x] Replace mock InsightsService with real Gemini AI — 2026-05-05
- [x] Wire all 3 frontend action handlers (dismiss, action, apply) — 2026-05-05
- [x] Fix ActionItem and Pattern TypeScript types — 2026-05-05

## In Progress
- [/] Run Alembic migration (requires Docker)

## Planned
- [ ] Add audit logging for policy CRUD operations
- [ ] Add policy versioning (track changes over time)
- [ ] Add policy testing ("dry-run" against sample data)

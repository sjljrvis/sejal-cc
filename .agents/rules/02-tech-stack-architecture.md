---
trigger: model_decision
description: Reference when making decisions about backend/frontend technology choices, folder structure, adding new services, or architectural patterns
---

# 1. Backend Tech Stack
- **Language:** Python 3.11
- **Framework:** FastAPI (async-capable, dependency injection)
- **ORM:** SQLAlchemy (with Alembic for migrations)
- **Database:** PostgreSQL 15
- **Server:** Gunicorn (multi-worker in production, single-worker with hot reload in dev)
- **AI SDK:** `google-genai` (>=1.51.0 — required for Gemini 3 features: `thinking_config`, `thought_signatures`, `media_resolution`). Always accessed through `app/services/ai/` abstraction layer.
- **Auth:** Keycloak 24 (OAuth2/OIDC) with pluggable RBAC/ABAC engine (`app/authz.py` + `authz.map.json`)

# 2. Frontend Tech Stack
- **Framework:** Next.js 15 (App Router), React 19, TypeScript (strict mode)
- **Styling:** Tailwind CSS v3 with custom `tailwind.config.js`
- **UI Primitives:** shadcn/ui (Radix-based: Dialog, Select, Switch, DropdownMenu, etc.)
- **Animation:** Framer Motion (scroll/sequence logic), Tailwind keyframes (simple loops)
- **Charts:** Recharts 3 with brand theme
- **Icons:** `lucide-react` (stroke-width 1.5)
- **Auth:** NextAuth.js v4 (session management, token refresh)
- **Output:** Must support `output: "standalone"` in `next.config.ts`.

# 3. Infrastructure
- **Local Dev:** Docker + Docker Compose (`make up` / `make down`)
- **Production:** Google Cloud Run + Cloud SQL (PostgreSQL)
- **Identity:** Keycloak hosted on Cloud Run

# 4. Backend Folder Responsibilities
- `/app/main.py`: FastAPI app, router mounting, middleware setup.
- `/app/routers/`: API endpoint definitions (thin — delegate to services).
- `/app/services/`: Business logic + AI abstraction layer (`services/ai/`).
- `/app/models/`: SQLAlchemy ORM models.
- `/app/schemas/`: Pydantic request/response schemas.
- `/app/core/`: Database connection, storage abstraction, logging config.
- `/app/middleware/`: Request middleware (audit logging).
- `/app/security.py` + `/app/authz.py`: Auth + authorization engine.
- `/app/services/ingestion/`: Data ingestion adapters (CSV, JSON, PDF, API). All external data enters here. See Rule 11.
- `/app/services/strategies/`: Documented exception patterns when policies can't handle logic. Last resort. See Rule 10.

# 5. Frontend Folder Responsibilities
- `/frontend/src/app/`: Next.js App Router pages, layouts, and route handlers.
- `/frontend/src/components/ui/`: Reusable shadcn/Radix UI primitives (Button, Card, Switch, etc.).
- `/frontend/src/components/[domain]/`: Domain-specific components (e.g., `ai/`, `admin/`, `layout/`).
- `/frontend/src/components/brand/`: Logo and branding components (Logomark, Logo, VisualPattern).
- `/frontend/src/lib/`: API client (`api-client.ts`), utility functions.
- `/frontend/src/context/`: React contexts (e.g., `AIContext.tsx`).
- `/frontend/src/hooks/`: Custom React hooks.

# 6. Architectural Rules
- Components must be functional and typed with TypeScript.
- **Size Limit:** If a component grows beyond ~250 lines, split it into smaller composable pieces.
- Never duplicate UI patterns. If you build a card twice, extract it to `/components/ui/`.
- **AI Abstraction:** Never import `google.genai` directly in routers or business logic. Always use `app/services/ai/`.
- **Background Tasks:** All slow operations (AI analysis, data processing, reports) must use background tasks.
---
trigger: model_decision
description: Reference when creating or modifying API endpoints, request/response schemas, pagination, filtering, or error handling patterns
---

# 1. RESTful URL Patterns
- Use **plural nouns** for resource collections: `/api/tickets`, `/api/policies`, `/api/users`.
- Use path parameters for specific resources: `/api/tickets/{ticket_id}`.
- Use nested routes sparingly and only for true parent-child relationships: `/api/tickets/{ticket_id}/comments`.
- Keep URLs **max 2 levels deep**. If deeper, flatten with query parameters.
- Use `kebab-case` for multi-word URL segments: `/api/audit-logs`, `/api/ai-insights`.

# 2. HTTP Methods
| Method | Purpose | Idempotent | Example |
|--------|---------|------------|---------|
| `GET` | Retrieve resource(s) | ✅ | `GET /api/tickets` |
| `POST` | Create new resource | ❌ | `POST /api/tickets` |
| `PUT` | Full update (replace) | ✅ | `PUT /api/tickets/{id}` |
| `PATCH` | Partial update | ✅ | `PATCH /api/tickets/{id}` |
| `DELETE` | Remove resource | ✅ | `DELETE /api/tickets/{id}` |

# 3. Standard Response Envelope
All API responses MUST follow a consistent structure.

### Success (single resource):
```json
{
  "data": { "id": "abc-123", "name": "..." },
  "message": "Ticket retrieved successfully"
}
```

### Success (collection):
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 142,
    "total_pages": 8
  }
}
```

### Error:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [ { "field": "email", "issue": "Invalid format" } ]
  }
}
```

# 4. Status Codes
Use the correct HTTP status code — never return 200 for errors.

| Code | When to Use |
|------|-------------|
| `200` | Successful GET, PUT, PATCH |
| `201` | Successful POST (resource created) |
| `204` | Successful DELETE (no content) |
| `400` | Bad request / validation error |
| `401` | Not authenticated |
| `403` | Authenticated but not authorized |
| `404` | Resource not found |
| `409` | Conflict (duplicate, state mismatch) |
| `422` | Unprocessable entity (valid JSON but semantically wrong) |
| `429` | Rate limited |
| `500` | Internal server error (unexpected) |

# 5. Pagination
All list endpoints MUST support pagination:
- **Query params:** `?page=1&page_size=20`
- **Defaults:** `page=1`, `page_size=20`
- **Max page size:** `100` (prevent abuse)
- Always return `pagination` object in the response.

# 6. Filtering & Sorting
- **Filtering:** Use query params matching field names: `?status=active&category=security`
- **Sorting:** `?sort_by=created_at&sort_order=desc`
- **Search:** `?search=keyword` for full-text search across relevant fields
- **Date ranges:** `?start_date=2025-01-01&end_date=2025-12-31`

# 7. Pydantic Schema Discipline
- Every endpoint MUST have explicit Pydantic request and response schemas in `/app/schemas/`.
- Never return raw SQLAlchemy model objects — always map to a response schema.
- Use `Optional[]` for nullable fields, never raw `None` types.
- Name schemas clearly: `TicketCreate`, `TicketUpdate`, `TicketResponse`, `TicketListResponse`.

# 8. Versioning
- No URL versioning for now (v1/v2). If breaking changes are needed, discuss with the team first.
- Use **additive changes** (new fields, new endpoints) over breaking changes wherever possible.

# 9. Router Organization
- One router file per domain entity in `/app/routers/`: `tickets.py`, `policies.py`, `users.py`.
- Router files are **thin** — they validate input, call services, and return responses.
- All business logic lives in `/app/services/`.
- Use FastAPI `tags` for Swagger grouping: `@router.get("/tickets", tags=["Tickets"])`.

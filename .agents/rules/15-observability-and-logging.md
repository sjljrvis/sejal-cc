---
trigger: model_decision
description: Reference when adding logging, configuring log levels, instrumenting AI calls or background tasks, building audit log entries, or debugging production issues.
---

# 1. Logging Goals
You log so that future-you (or oncall) can answer:
- **What just happened?** (event type, who, when, on what)
- **Why did it fail?** (error class, stack frame, input shape)
- **How long did it take?** (duration, queue time)
- **Did it cost money?** (AI tokens, external API calls, big queries)

If a log line doesn't help with one of those, don't write it.

# 2. Levels — Use Them Correctly
| Level | When | Examples |
|---|---|---|
| `DEBUG` | Local dev, deep tracing | Variable dumps, intermediate AI prompt segments |
| `INFO` | Normal events worth recording | Request handled, ingestion run completed, policy evaluated |
| `WARNING` | Recoverable anomaly that someone might want to know | Retry succeeded after first failure, deprecated field used |
| `ERROR` | Operation failed, user impact, but app continues | AI rate-limited after retries, ingestion record quarantined |
| `CRITICAL` | App-level failure, oncall should look | DB connection lost, auth subsystem down |

**Never log at INFO inside hot loops.** If you're logging once per record in a 50K-record ingestion, you're flooding the logs. Aggregate to a summary at the end.

# 3. Structured Logging
Logs are read by humans and by tools. Use structured JSON in production, key=value in dev.

```python
# ❌ BAD: unstructured, can't be queried
logger.info(f"Ticket {ticket_id} approved by {user_email} after {ms}ms")

# ✅ GOOD: structured fields
logger.info(
    "ticket.approved",
    extra={"ticket_id": ticket_id, "user_id": user.id, "duration_ms": ms},
)
```

Event names are dotted lowercase nouns: `ticket.approved`, `policy.evaluated`, `ingestion.run.completed`, `ai.call.failed`. Searching for `event=ticket.approved` should return all approval events across services.

# 4. What to Log Per Subsystem

### Request handling (FastAPI middleware)
- One INFO per request: `http.request` with method, path, status, duration_ms, user_id (if authenticated). The audit middleware (`docs/Audit System Guide.md`) handles this — don't duplicate it in handlers.

### AI calls (Rule 06)
One log line per AI call:
```
ai.call.started   { model, prompt_tokens_estimate, tool_count }
ai.call.completed { model, prompt_tokens, output_tokens, duration_ms, finish_reason }
ai.call.failed    { model, error_class, retry_count, duration_ms }
```
- Mask sensitive fields in the input (PII, secrets — Rule 13 §5).
- Token counts are a cost signal — log them every time.

### Policy evaluation (Rule 06 §6)
```
policy.evaluated { entity_type, entity_id, policy_count, matched_count, modified_fields }
```
Don't log the full policy DSL on every evaluation — log it once at policy load, and reference by ID afterward.

### Background tasks
```
task.started   { task_name, task_id, params_summary }
task.completed { task_name, task_id, duration_ms, items_processed }
task.failed    { task_name, task_id, duration_ms, error_class }
```

### Ingestion (Rule 11)
End-of-run summary at INFO:
```
ingestion.run.completed { adapter, total, ingested, failed, quarantined, duration_ms }
```
Per-record errors at WARNING with the record ID — never log the full raw record (may contain PII, may be huge).

# 5. Sensitive Field Masking (CRITICAL)
A log line is forever. PII and secrets must be masked at the logger level, not at every call site.

Maintain a **mask list** of field names: `password`, `api_key`, `token`, `authorization`, `email`, `phone`, `ssn`, `date_of_birth`, `address`, `salary`, `account_number`. The structured logger replaces them with `***`.

For free-text fields that may contain PII (ticket descriptions, email bodies), the AI service redaction layer runs first; the logger then trusts the result.

# 6. Audit Logging vs. App Logging
These are different streams. Don't confuse them.

- **App logs** (this rule): debugging, performance, errors. Ephemeral, retained ~30 days, not legally significant.
- **Audit logs** (`docs/Audit System Guide.md`): immutable record of who did what, when, on what entity. Retained per compliance requirements. Goes through the audit middleware, persisted to DB.

When in doubt: if a regulator or auditor would care, it's an audit log. If only oncall cares, it's an app log.

# 7. Errors & Stack Traces
- Always log exceptions with `logger.exception("event.name", extra={...})` — that captures the stack frame.
- For caught exceptions where you handle gracefully (e.g., AI rate limit → retry), log at WARNING the first attempt, ERROR if all retries fail.
- Never let a stack trace reach the user. The router returns the standard error envelope (Rule 08 §3); the trace stays in logs.
- Include a correlation ID (request ID) in every log line so a user-facing error can be traced back to the exact lines.

# 8. Performance Signals
Log duration for any operation that *could* be slow:
- AI calls (always)
- DB queries that touch >1K rows
- External HTTP calls
- Background task end-to-end
- Ingestion runs

Use a single `duration_ms` field name everywhere — consistency lets you query and chart.

# 9. Local Dev Logging
- `APP_ENV=development` → human-readable format with colors. Levels at `DEBUG`.
- `APP_ENV=production` → JSON format. Levels at `INFO`.

If you find yourself adding `print()` to debug, you're doing it wrong — use `logger.debug()` with `extra={...}`. Print statements get committed by accident; logger calls survive review.

# 10. Pre-Commit Logging Self-Check
- [ ] No `print()` or `console.log()` in tracked code (Rule 04 §4).
- [ ] New events use the `subject.action` naming convention (§3).
- [ ] No raw PII or secrets in log fields (§5).
- [ ] Errors logged with `logger.exception` and a correlation ID (§7).
- [ ] AI calls log token counts and duration (§4).
- [ ] Hot loops aggregate to a summary instead of per-iteration INFO (§2).

---
trigger: model_decision
description: Reference when implementing AI features, integrating Gemini, creating AI tools, working with AI policies, or configuring prompts
---

# 1. AI Abstraction Layer (MANDATORY)
All AI interactions go through `app/services/ai/`. This directory contains:
- The Gemini API client (wraps `google.genai`, version `>=1.51.0` for Gemini 3 features)
- AI Manager / Copilot chat logic
- Policy translation (natural language → DSL)
- Tool definitions for function calling

**NEVER** import `google.genai` directly in routers, middleware, or non-AI services. Always go through the abstraction layer so models can be swapped without rewriting business logic.

When creating new AI capabilities for this use case, follow the existing patterns in `app/services/ai/` and add new modules there. Subclass `GeminiService` and use its `_get_text_config` / `_get_json_config` / `_get_structured_config` helpers — do not construct `GenerateContentConfig` from scratch, you'll miss `thinking_config` and the SDK upgrades that go through the base.

# 2. Model Configuration (Gemini 3 — 2026)
- **Default Model:** `gemini-3-flash-preview` via `AI_MODEL` env var.
  - Stable / cheapest: `gemini-3.1-flash-lite`
  - Top reasoning: `gemini-3.1-pro-preview`
  - **Deprecated:** `gemini-2.5-flash` (still works); `gemini-2.0-flash*` shuts down 2026-06-01 — do not introduce new code paths against it.
- **Thinking Level:** Set via `AI_THINKING_LEVEL` (default `medium`). One of `minimal | low | medium | high`. Pass `thinking_level=` to `_get_*_config()` to override per-call (e.g. `low` for chat, `high` for `RuleArchitect`).
- **Temperature:** Do **not** set `temperature` explicitly on Gemini 3. The default of 1.0 is what Google recommends; explicit low values cause looping / degradation on complex prompts.
- **Concurrency:** Respect `AI_CONCURRENCY_LIMIT` (default 18) for parallel AI calls.
- **API Key:** `GEMINI_API_KEY` env var. The base `GeminiService` checks existence on construction — never duplicate this check in subclasses.

# 3. Prompt Engineering Rules
- **System Prompts:** Store as named constants or dedicated files — never inline strings scattered across code.
- **Structured Output:** Use `_get_structured_config(MyPydanticSchema)` — that wires `response_json_schema` so the model output round-trips through Pydantic with no regex.
- **Few-Shot Examples:** Include for complex tasks (classification, data extraction, entity recognition). Gemini 3 with `thinking_level=high` often needs fewer few-shots than the 2.x equivalents — start minimal.
- **Prompt Style:** Gemini 3 is a reasoning model. Keep prompts short and direct; verbose chain-of-thought instructions can confuse it. Anchor it: "Based on the data above, ..." beats long preambles.
- **Token Awareness:** Input context is 1M tokens, output cap 64k. `media_resolution` controls token usage for image/PDF/video parts (`media_resolution_low | medium | high`).

# 4. Tool Calling (Function Calling) Pattern
Follow the established pattern in `app/services/ai/tools.py`:
1. **Define tools** with `genai_types.Tool(function_declarations=[...])`.
2. **Pass tool list** to the model via `_get_text_config(tools=...)`.
3. **AI decides** which tool to call and with what arguments.
4. **Backend executes** the chosen function.
5. **Append `candidate.content` verbatim** to history before sending the function response back. Then add `Content(role="user", parts=[Part.from_function_response(...)])`.

**Gemini 3 — Strict thought_signature contract (CRITICAL):**
- Every model turn that emits a `function_call` carries an encrypted `thought_signature` part.
- On the **next** turn you MUST send the model's full Content back. Reconstructing it from `.text` strips the signature and Gemini 3 returns **HTTP 400 "missing thought_signature"**.
- The official `google-genai` SDK preserves signatures automatically when you `contents.append(candidate.content)`. Do not refactor that to a text-only rebuild.
- For parallel function calls, only the first part carries the signature — keep the parts list intact.

**Built-in tools (Gemini 3, optional):** `{"google_search": {}}`, `{"url_context": {}}`, `{"code_execution": {}}`, `{"maps": {}}`. These can now be combined with custom function declarations in the same request.

# 5. Error Handling (CRITICAL)
All AI calls MUST be wrapped in try/except:
- Handle **rate limits** (429) with exponential backoff.
- Handle **token limit exceeded** by truncating input and retrying.
- Handle **malformed responses** with fallback logic.
- Handle **`thought_signature` 400 errors** distinctly — the fix is in history-construction code, not in prompts. `app/services/ai/chat.py` has a precedent: detect `"thought_signature"` in the error string and log a fix-the-history hint.
- **Log AI inputs/outputs** for debugging — mask any sensitive data (PII, API keys).
- Never let an AI error crash the API. Return a graceful error message to the frontend.

# 6. AI Policies Engine
- Rules stored in the `Policies` DB table with JSON `conditions` field.
- The Rule Evaluator service fetches and evaluates rules against input data.
- Natural language → DSL translation is a core feature. Use structured output mode for translations.
- Always validate translated DSL before persisting.

# 7. Background Processing (CRITICAL)
- **All AI analysis, batch operations, and report generation** must use background tasks.
- API responses must stay fast (< 2 seconds). If an AI operation takes longer, return a task ID and use WebSocket or polling for progress updates.
- Use FastAPI's `BackgroundTasks` dependency for async operations. If a dedicated task manager is needed, create it in `app/core/`.

# 8. Policy-First Business Logic (CRITICAL)
ALL domain decisions MUST go through AI Policies — either as structured DSL (via `RuleEngine`) or natural language (via `PolicyService`). See Rule 10 for the complete enforcement protocol, fallback hierarchy, and anti-pattern detection.

**Mandatory RuleArchitect usage:** When creating any new AI Policy, the `RuleArchitect` service (`app/services/rule_architect.py`) MUST be used to:
- Check for **conflicts** with existing policies
- Detect **overrides** (INSTRUCTION rules overriding BASE rules)
- Generate **clarifications** and **refined instructions**

This is not optional — every policy creation flow must include conflict analysis.

**Policy evaluation points:** Every new domain entity MUST define where in its lifecycle AI Policies should fire:
- On ingestion (validate/classify)
- On status change (approval/rejection/escalation)
- On assignment (routing)
- On threshold (limits/quotas)
- On schedule (SLA checks)

Document these in `docs/{use-case}.md`.

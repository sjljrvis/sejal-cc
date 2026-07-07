# Active Context

## Currently Working On
Gemini 3 migration — backend AI stack updated end-to-end.

## Current State
- All AI services (`gemini.py`, `policy.py`, `insights.py`, `chat.py`, `rule_architect.py`) now run on `google-genai>=1.51.0` with Gemini 3 defaults.
- New env: `AI_MODEL=gemini-3-flash-preview` (default), `AI_THINKING_LEVEL=medium` (default), `AI_FALLBACK_MODEL` (optional).
- All explicit `temperature=0.1/0.2/0.3/0.7` overrides removed (Gemini 3 default 1.0 is recommended; low values cause looping).
- `RuleArchitect` and `PromptOptimizer` now subclass `GeminiService` — single source of truth for client + model config.
- `chat.py` preserves `thought_signature` parts on every tool-call turn (verbatim `candidate.content` append) and surfaces missing-signature 400 errors with a fix-the-history hint.
- API-key leak in `scripts/test_ai.py` removed from working tree.
- Lint clean on every file we touched. Pre-existing `F401` in `app/services/ai/rule_engine.py` left as-is (not in this PR's scope).

## Immediate Next Steps
1. Confirm and execute `git filter-repo` to scrub the leaked key from history (destructive — needs explicit yes).
2. After scrub: rotate the leaked Gemini key at https://aistudio.google.com/apikey, paste fresh value into local `.env`.
3. `make up` → `make migrate-up` → run `python scripts/test_ai.py` against live Gemini 3.
4. Watch Insights run with `AI_THINKING_LEVEL=medium` — measure latency vs old 2.5 baseline.

## Blockers
- Awaiting final user confirmation before history rewrite + force push of `main`.
- Docker not running locally — migration + live AI tests pending.

## Recent Changes
1. `app/services/ai/gemini.py` — rewritten as Gemini-3 base service (thinking_config, structured/json/text config helpers).
2. `app/services/ai/policy.py` — uses base helpers; explicit `thinking_level="low"` per call.
3. `app/services/ai/insights.py` — uses `_get_json_config`; thinking_level defaults to env (`medium`).
4. `app/services/ai/chat.py` — `thought_signature`-safe tool loop, distinct error handling for missing-signature 400s.
5. `app/services/rule_architect.py` — `RuleArchitect`/`PromptOptimizer` now subclass `GeminiService`; conflict analysis pinned to `thinking_level="high"`.
6. `scripts/test_ai.py` — leaked literal removed; reads from env.
7. `.env.example`, `docker-compose.yml`, `packages/requirements.txt` — Gemini 3 defaults + SDK floor.
8. `README.md`, `.agents/rules/{02,06,07,13}` — docs synced.
9. `docs/memory-bank/decisionLog.md` — two new rows logged.

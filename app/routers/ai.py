"""
Supervity AI Router - API endpoints for AI features (chat, policies, insights)

Policies are now stored in the database (not in-memory).
Demo data is seeded via the /policies/seed-demo endpoint.
"""

import asyncio
import logging
import os
import time
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.security import get_current_user
from app.schemas.ai import (
    ChatRequest, ChatResponse,
    PolicyCreate, PolicyUpdate, PolicyResponse, PolicyDSL, PolicyType, PolicyScopeEnum,
    PolicyTranslateRequest, PolicyTranslateResponse,
    PolicyAnalyzeRequest, PolicyAnalyzeResponse,
    InsightsListResponse, AnalyzeRequest
)
from app.services.ai import ai_service, policy_service
from app.services.rule_architect import rule_architect, prompt_optimizer
from app.services.policy_crud import policy_crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])


# ============================================================================
# Chat Endpoints
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the AI assistant.
    Supports conversational context and function calling.
    """
    try:
        response = await ai_service.chat_message(
            message=request.message,
            history=request.history,
            context=request.context,
            user_id=current_user.get("sub")
        )
        return response
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")


# ============================================================================
# Policy Endpoints — Database-backed
# ============================================================================

# Concurrency limit for parallel AI processing (from environment)
AI_CONCURRENCY_LIMIT = int(os.getenv("AI_CONCURRENCY_LIMIT", "4"))

# Import demo data from centralized seed script
try:
    from scripts.seed_ai_demo import (
        DEMO_POLICY_INPUTS,
        DEMO_PATTERNS,
        DEMO_ACTIONS,
        get_demo_insights,
    )
    _SEED_SCRIPT_AVAILABLE = True
except ImportError:
    _SEED_SCRIPT_AVAILABLE = False
    DEMO_POLICY_INPUTS = [
        {"input": "If an invoice is less than $500 from an approved vendor, auto-approve payment", "category": "finance", "priority": 10},
        {"input": "Transactions over $50,000 require CFO approval", "category": "finance", "priority": 5},
    ]
    DEMO_PATTERNS = []
    DEMO_ACTIONS = []
    def get_demo_insights():
        return []


def _generate_ai_instruction(policy_type: str, dsl: Optional[dict], refined_instruction: Optional[str], natural_language: str) -> str:
    """Generate the AI instruction based on policy type."""
    if policy_type == "natural_language":
        return refined_instruction or natural_language

    if dsl and dsl.get("conditions"):
        conditions = dsl.get("conditions", [])
        actions = dsl.get("actions", [])
        match_mode = dsl.get("match_mode", "all")

        cond_strs = []
        for c in conditions:
            field = c.get("field", "?")
            op = c.get("operator", "eq")
            val = c.get("value")
            op_map = {"eq": "=", "neq": "!=", "gt": ">", "lt": "<", "gte": ">=", "lte": "<=", "in": "IN", "contains": "CONTAINS"}
            op_str = op_map.get(op, op)
            cond_strs.append(f"{field} {op_str} {val}")

        joiner = " AND " if match_mode == "all" else " OR "
        condition_text = joiner.join(cond_strs)

        action_strs = [a.get("type", "?") + (f"('{a.get('value')}')" if a.get("value") else "") for a in actions]
        action_text = ", ".join(action_strs)

        return f"IF {condition_text} THEN {action_text}"

    return natural_language


# ============================================================================
# Seed Demo Policies
# ============================================================================

@router.post("/policies/seed-demo")
async def seed_demo_policies_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Seed demo policies by processing each natural language input through AI.
    Clears existing demo policies first, then creates new ones.
    """
    # Clear existing demo policies
    deleted = policy_crud.delete_by_source(db, "demo")
    logger.info(f"Cleared {deleted} existing demo policies")

    now = datetime.now(timezone.utc)
    total = len(DEMO_POLICY_INPUTS)
    logger.info(f"🚀 Seeding {total} demo policies with AI analysis (parallel, max {AI_CONCURRENCY_LIMIT} concurrent)...")

    semaphore = asyncio.Semaphore(AI_CONCURRENCY_LIMIT)
    results = []

    async def process_one(index: int, demo: dict):
        policy_id = f"demo-policy-{index + 1:03d}"

        if isinstance(demo, dict):
            natural_language = demo.get("input", str(demo))
            category = demo.get("category", "general")
            priority = demo.get("priority", (index + 1) * 10)
        else:
            natural_language = str(demo)
            category = "general"
            priority = (index + 1) * 10

        async with semaphore:
            try:
                analysis = await policy_service.analyze(natural_language)

                dsl_dict = analysis.dsl.model_dump() if analysis.dsl else None
                ai_instruction = _generate_ai_instruction(
                    analysis.policy_type, dsl_dict, analysis.refined_instruction, natural_language
                )

                data = {
                    "id": policy_id,
                    "name": analysis.suggested_name,
                    "description": f"AI-generated from natural language. Category: {category}. [DEMO]",
                    "summary": analysis.summary,
                    "original_input": natural_language,
                    "policy_type": analysis.policy_type,
                    "policy_scope": "base",
                    "dsl": dsl_dict,
                    "refined_instruction": analysis.refined_instruction,
                    "ai_instruction": ai_instruction,
                    "entity_name": analysis.entity_name,
                    "is_active": True,
                    "priority": priority,
                    "tags": list(set((analysis.suggested_tags or []) + [category, "demo", "ai-generated"])),
                    "source": "demo",
                    "execution_count": (8 - index) * 15 if index < 8 else 10,
                    "last_executed_at": now - timedelta(hours=index + 1),
                    "created_at": now - timedelta(days=30 - index * 3),
                    "updated_at": now - timedelta(hours=index * 2),
                }

                logger.info(f"  ✓ [{index + 1}] {analysis.suggested_name} ({analysis.policy_type}, {analysis.confidence:.0%})")
                return data

            except Exception as e:
                logger.error(f"  ✗ [{index + 1}] Failed: {e}")
                return {
                    "id": policy_id,
                    "name": f"Policy {index + 1}",
                    "description": f"Demo policy - {category} (AI unavailable)",
                    "summary": natural_language[:100],
                    "original_input": natural_language,
                    "policy_type": "natural_language",
                    "policy_scope": "base",
                    "dsl": None,
                    "refined_instruction": natural_language,
                    "ai_instruction": natural_language,
                    "entity_name": None,
                    "is_active": True,
                    "priority": priority,
                    "tags": [category, "demo", "needs-review"],
                    "source": "demo",
                    "execution_count": 0,
                    "last_executed_at": None,
                    "created_at": now - timedelta(days=30 - index * 3),
                    "updated_at": now,
                }

    start_time = time.time()
    tasks = [process_one(i, demo) for i, demo in enumerate(DEMO_POLICY_INPUTS)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    elapsed = time.time() - start_time

    # Persist to database
    success_count = 0
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"  ✗ Task failed: {result}")
        elif isinstance(result, dict):
            try:
                policy_crud.create(db, data=result)
                success_count += 1
            except Exception as e:
                logger.error(f"  ✗ DB write failed for {result.get('id')}: {e}")

    logger.info(f"✅ Seeded {success_count}/{total} demo policies in {elapsed:.2f}s")

    return {
        "message": f"Seeded {success_count} demo policies with AI analysis",
        "policies": [
            {"id": r.get("id"), "name": r.get("name"), "type": r.get("policy_type")}
            for r in results if isinstance(r, dict)
        ]
    }


# ============================================================================
# Policy CRUD — Database-backed
# ============================================================================

@router.get("/policies", response_model=List[PolicyResponse])
async def list_policies(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    policy_type: Optional[str] = Query(None, description="Filter by type (logical, natural_language)"),
    search: Optional[str] = Query(None, description="Search policies"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all AI policies from the database."""
    policies = policy_crud.list(
        db,
        is_active=is_active,
        policy_type=policy_type,
        search=search,
    )

    return [PolicyResponse(**p.to_dict()) for p in policies]


@router.post("/policies", response_model=PolicyResponse, status_code=201)
async def create_policy(
    policy: PolicyCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new AI policy with full AI analysis pipeline.

    Flow:
    1. If user provided DSL → use logical type directly
    2. If user explicitly set policy_type → honor it
    3. Otherwise → let AI analyze and decide everything

    After type detection, conflict detection runs against existing policies.
    """
    policy_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    original_input = policy.original_input

    # --- Determine policy type and generate DSL/instruction ---
    if policy.dsl:
        # User explicitly provided DSL
        policy_type = "logical"
        dsl = policy.dsl
        dsl_dict = dsl.model_dump()
        refined_instruction = policy.refined_instruction
        summary = policy.summary
        entity_name = policy.entity_name
        tags = policy.tags or []
    elif policy.policy_type:
        # User explicitly chose a type
        policy_type = policy.policy_type.value
        dsl = None
        dsl_dict = None
        refined_instruction = policy.refined_instruction or original_input
        summary = policy.summary
        entity_name = policy.entity_name
        tags = policy.tags or []

        if policy_type == "logical":
            try:
                translation = await policy_service.translate(original_input)
                dsl = translation.dsl
                dsl_dict = dsl.model_dump() if dsl else None
            except Exception as e:
                logger.warning(f"DSL translation failed: {e}")
    else:
        # Full AI analysis
        analysis = await policy_service.analyze(
            natural_language=original_input,
        )

        policy_type = analysis.policy_type
        dsl = analysis.dsl
        dsl_dict = dsl.model_dump() if dsl else None
        refined_instruction = analysis.refined_instruction or original_input
        summary = analysis.summary
        entity_name = analysis.entity_name or policy.entity_name
        tags = analysis.suggested_tags or policy.tags or []

        logger.info(f"AI analysis: type={policy_type}, confidence={analysis.confidence:.2f}, reason='{analysis.reason}'")

    # Ensure refined instruction exists for NL type
    if policy_type == "natural_language" and not refined_instruction:
        try:
            refined_instruction = await policy_service.refine_instruction(original_input)
        except Exception as e:
            logger.warning(f"Instruction refinement failed: {e}")
            refined_instruction = original_input

    # Generate summary if missing
    if not summary:
        try:
            summary = await policy_service.generate_summary(original_input)
        except Exception as e:
            logger.warning(f"Summary generation failed: {e}")
            summary = original_input[:97] + "..." if len(original_input) > 100 else original_input

    ai_instruction = _generate_ai_instruction(policy_type, dsl_dict, refined_instruction, original_input)

    # --- Run conflict detection ---
    conflict_analysis = None
    try:
        existing_policies = policy_crud.list_active(db)
        existing_rules = [p.to_dict() for p in existing_policies]

        if existing_rules:
            conflict_analysis = await rule_architect.analyze_rule(
                new_rule={
                    "natural_language": original_input,
                    "policy_type": policy.policy_scope.value,
                    "entity_name": entity_name,
                },
                existing_rules=existing_rules,
                entity_name=entity_name,
            )

            if conflict_analysis and conflict_analysis.conflicts:
                logger.warning(
                    f"Policy conflicts detected: {len(conflict_analysis.conflicts)} conflicts"
                )
    except Exception as e:
        logger.warning(f"Conflict detection failed (non-blocking): {e}")

    # --- Persist to database ---
    policy_data = {
        "id": policy_id,
        "name": policy.name,
        "description": policy.description or "",
        "summary": summary,
        "original_input": original_input,
        "policy_type": policy_type,
        "policy_scope": policy.policy_scope.value,
        "dsl": dsl_dict,
        "refined_instruction": refined_instruction,
        "ai_instruction": ai_instruction,
        "entity_name": entity_name,
        "is_active": policy.is_active,
        "priority": policy.priority,
        "tags": tags,
        "source": "user",
    }

    db_policy = policy_crud.create(
        db,
        data=policy_data,
        created_by=current_user.get("sub"),
    )

    response = PolicyResponse(**db_policy.to_dict())

    return response


@router.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific policy by ID."""
    policy = policy_crud.get(db, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    return PolicyResponse(**policy.to_dict())


@router.patch("/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    policy: PolicyUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing policy.

    If original_input (natural_language) changes, re-run AI analysis
    to regenerate DSL, refined_instruction, summary, and ai_instruction.
    """
    existing = policy_crud.get(db, policy_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_data = policy.model_dump(exclude_unset=True)

    # If natural language changed, re-analyze
    nl_changed = "original_input" in update_data and update_data["original_input"] != existing.original_input
    if nl_changed:
        new_input = update_data["original_input"]
        try:
            analysis = await policy_service.analyze(natural_language=new_input)

            update_data["policy_type"] = update_data.get("policy_type", analysis.policy_type)
            if analysis.dsl and update_data.get("policy_type", analysis.policy_type) == "logical":
                update_data["dsl"] = analysis.dsl.model_dump()
            update_data["refined_instruction"] = analysis.refined_instruction or new_input
            update_data["summary"] = analysis.summary
            update_data["entity_name"] = update_data.get("entity_name") or analysis.entity_name
            if analysis.suggested_tags:
                existing_tags = update_data.get("tags", existing.tags or [])
                update_data["tags"] = list(set(existing_tags + analysis.suggested_tags))

            dsl_dict = update_data.get("dsl")
            update_data["ai_instruction"] = _generate_ai_instruction(
                update_data.get("policy_type", existing.policy_type),
                dsl_dict,
                update_data.get("refined_instruction"),
                new_input,
            )

            logger.info(f"Re-analyzed policy {policy_id}: type={analysis.policy_type}")
        except Exception as e:
            logger.warning(f"Re-analysis failed for {policy_id}: {e}")

    # Handle DSL serialization
    if "dsl" in update_data and update_data["dsl"] is not None:
        if hasattr(update_data["dsl"], "model_dump"):
            update_data["dsl"] = update_data["dsl"].model_dump()

    # Handle enum serialization
    if "policy_type" in update_data and hasattr(update_data["policy_type"], "value"):
        update_data["policy_type"] = update_data["policy_type"].value
    if "policy_scope" in update_data and update_data["policy_scope"] is not None:
        if hasattr(update_data["policy_scope"], "value"):
            update_data["policy_scope"] = update_data["policy_scope"].value

    updated = policy_crud.update(db, policy_id, data=update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Policy not found")

    return PolicyResponse(**updated.to_dict())


@router.delete("/policies/{policy_id}", status_code=204)
async def delete_policy(
    policy_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a policy."""
    if not policy_crud.delete(db, policy_id):
        raise HTTPException(status_code=404, detail="Policy not found")


# ============================================================================
# Policy Analysis Endpoints
# ============================================================================

@router.post("/policies/translate", response_model=PolicyTranslateResponse)
async def translate_policy(
    request: PolicyTranslateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Translate natural language policy description to structured DSL."""
    try:
        result = await ai_service.translate_policy(request.natural_language)
        return result
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to translate policy")


@router.post("/policies/analyze-input", response_model=PolicyAnalyzeResponse)
async def analyze_policy_input(
    request: PolicyAnalyzeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze a natural language policy input using AI.
    Returns type suggestion, DSL, refined instruction, tags, etc.
    This is the first step in the guided policy creation wizard.
    """
    input_text = request.input.strip()

    if not input_text:
        raise HTTPException(status_code=400, detail="Policy input cannot be empty")

    user_preferred_type = None
    if hasattr(request, 'preferred_type') and request.preferred_type:
        user_preferred_type = request.preferred_type

    try:
        analysis = await policy_service.analyze(
            natural_language=input_text,
            user_preferred_type=user_preferred_type
        )

        return PolicyAnalyzeResponse(
            suggested_type=PolicyType(analysis.policy_type),
            confidence=analysis.confidence,
            reason=analysis.reason,
            suggested_name=analysis.suggested_name,
            summary=analysis.summary,
            dsl=analysis.dsl,
            refined_instruction=analysis.refined_instruction,
            entity_name=analysis.entity_name,
            suggested_tags=analysis.suggested_tags or []
        )

    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return PolicyAnalyzeResponse(
            suggested_type=PolicyType.NATURAL_LANGUAGE,
            confidence=0.3,
            reason=f"AI analysis encountered an error: {str(e)}. Using fallback.",
            suggested_name="New Policy",
            summary=input_text[:97] + "..." if len(input_text) > 100 else input_text,
            dsl=None,
            refined_instruction=input_text,
            entity_name=None,
            suggested_tags=["needs-review"]
        )


@router.post("/policies/check-conflicts")
async def check_policy_conflicts(
    request: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check a new policy for conflicts against existing policies.

    Returns:
    - conflicts: Rules that contradict the new rule
    - overrides: BASE rules that will be overridden by this INSTRUCTION
    - clarifications: Questions to make the rule more precise
    - suggested_instructions: AI-refined versions of the rule
    - refined_instruction: The best refined instruction
    """
    try:
        natural_language = request.get("natural_language", "")
        policy_scope = request.get("policy_scope", "base")
        entity_name = request.get("entity_name")

        # Get existing rules from DB
        existing_policies = policy_crud.list_active(db)
        existing_rules = [p.to_dict() for p in existing_policies]

        # Analyze with Rule Architect
        analysis = await rule_architect.analyze_rule(
            new_rule={
                "natural_language": natural_language,
                "policy_type": policy_scope,
                "entity_name": entity_name
            },
            existing_rules=existing_rules,
            entity_name=entity_name
        )

        return analysis.to_dict()

    except Exception as e:
        logger.error(f"Policy conflict check error: {e}")
        refined = await prompt_optimizer.refine(request.get("natural_language", ""))
        return {
            "conflicts": [],
            "overrides": [],
            "clarifications": [],
            "suggested_instructions": [refined],
            "refined_instruction": refined,
            "is_valid": True,
            "warnings": [str(e)]
        }


# Keep the old /analyze endpoint for backward compatibility
@router.post("/policies/analyze")
async def analyze_policy(
    request: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a new policy for conflicts (backward-compatible endpoint).
    Delegates to check_policy_conflicts.
    """
    return await check_policy_conflicts(request, current_user, db)


# ============================================================================
# Insights Endpoints — Database-backed
# ============================================================================

from app.services.insight_crud import insight_crud


@router.post("/insights/seed-demo")
async def seed_demo_insights(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seed demo insights into the database. Clears existing demo data first."""
    deleted = insight_crud.delete_by_source(db, "demo")
    logger.info(f"Cleared {deleted} existing demo insights")

    demo_insights = get_demo_insights()
    for insight in demo_insights:
        insight["source"] = "demo"
        if "[DEMO]" not in insight.get("title", ""):
            insight["title"] = insight.get("title", "") + " [DEMO]"

    count = insight_crud.bulk_create(db, items=demo_insights)
    logger.info(f"Seeded {count} demo insights")

    # Also seed patterns and actions as special insight records
    for p in DEMO_PATTERNS:
        insight_crud.create(db, data={
            "type": "pattern",
            "severity": "info",
            "title": p.get("name", "Pattern"),
            "description": p.get("description", ""),
            "data": {"frequency": p.get("frequency"), "sample_size": p.get("sample_size"), "confidence": p.get("confidence")},
            "confidence": p.get("confidence", 0.8),
            "source": "demo",
        })

    return {"message": f"Seeded {count} demo insights + {len(DEMO_PATTERNS)} patterns"}


@router.get("/insights", response_model=InsightsListResponse)
async def list_insights(
    batch_id: Optional[str] = Query(None, description="Filter by batch ID"),
    type: Optional[str] = Query(None, description="Filter by type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    include_dismissed: bool = Query(False, description="Include dismissed insights"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get insights from the database. Seeds demo data if empty."""
    # Auto-seed demo data if table is empty
    total = insight_crud.count(db, include_dismissed=True)
    if total == 0:
        demo_insights = get_demo_insights()
        for insight in demo_insights:
            insight["source"] = "demo"
            if "[DEMO]" not in insight.get("title", ""):
                insight["title"] = insight.get("title", "") + " [DEMO]"
        insight_crud.bulk_create(db, items=demo_insights)
        logger.info(f"Auto-seeded {len(demo_insights)} demo insights on first access")

    db_insights = insight_crud.list(
        db,
        type=type,
        severity=severity,
        batch_id=batch_id,
        include_dismissed=include_dismissed,
    )

    # Separate pattern-type insights for the patterns list
    insight_records = []
    pattern_records = []

    for ins in db_insights:
        d = ins.to_dict()
        insight_records.append(d)
        if ins.type == "pattern":
            pattern_records.append({
                "name": ins.title,
                "frequency": (ins.data or {}).get("frequency", "ongoing"),
                "confidence": ins.confidence,
                "sample_size": (ins.data or {}).get("sample_size", 0),
                "description": ins.description,
            })

    # Build action recommendations from actionable insights
    action_records = []
    for ins in db_insights:
        if ins.action_type and ins.suggested_action and not ins.is_actioned:
            sev = ins.severity
            priority = "high" if sev in ("critical", "high") else "medium" if sev in ("warning", "medium") else "low"
            action_records.append({
                "title": ins.suggested_action,
                "priority": priority,
                "estimated_impact": f"Confidence: {ins.confidence:.0%}",
                "action_type": ins.action_type,
                "action_config": {"insight_id": ins.id},
            })

    return InsightsListResponse(
        insights=insight_records,
        patterns=pattern_records,
        actions=action_records,
        total_count=len(insight_records),
        generated_at=datetime.now(timezone.utc),
        analysis_duration_ms=0.5,
    )


@router.post("/insights/analyze", response_model=InsightsListResponse)
async def analyze_data(
    request: AnalyzeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger AI analysis on data and persist results."""
    try:
        result = await ai_service.generate_insights(
            batch_id=request.batch_id,
            date_range_start=request.date_range_start,
            date_range_end=request.date_range_end
        )

        # Persist AI-generated insights
        if result.insights:
            for ins in result.insights:
                ins_data = ins if isinstance(ins, dict) else ins.model_dump() if hasattr(ins, 'model_dump') else dict(ins)
                ins_data["source"] = "ai"
                ins_data["batch_id"] = request.batch_id
                try:
                    insight_crud.create(db, data=ins_data)
                except Exception as e:
                    logger.warning(f"Failed to persist insight: {e}")

        return result
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze data")


@router.patch("/insights/{insight_id}/dismiss")
async def dismiss_insight(
    insight_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dismiss an insight (hide from default view)."""
    result = insight_crud.dismiss(db, insight_id, user_id=current_user.get("sub"))
    if not result:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {"id": insight_id, "is_dismissed": True}


@router.patch("/insights/{insight_id}/action")
async def action_insight(
    insight_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an insight as actioned."""
    result = insight_crud.mark_actioned(db, insight_id, user_id=current_user.get("sub"))
    if not result:
        raise HTTPException(status_code=404, detail="Insight not found")
    return {"id": insight_id, "is_actioned": True}


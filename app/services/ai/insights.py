"""
Supervity AI Insights Service - AI-powered data analysis and insights generation

Uses Gemini AI to analyze data and generate actionable insights.
Falls back to heuristic analysis when AI is unavailable.
"""

import json
import time
import logging
from typing import Optional, List
from datetime import datetime, timezone

from google.genai import types as genai_types

from app.schemas.ai import (
    InsightsListResponse, InsightResponse, InsightType, InsightSeverity,
    PatternInfo, ActionRecommendation
)
from .gemini import GeminiService

logger = logging.getLogger(__name__)

INSIGHTS_SYSTEM_PROMPT = """You are the Supervity AI Insights Engine. Analyze the provided data and generate actionable insights.

**Generate insights in these categories:**
- PATTERN: Recurring behaviors or trends in the data
- ANOMALY: Unusual deviations from expected patterns
- RECOMMENDATION: Optimization opportunities
- TREND: Directional changes over time
- ALERT: Urgent issues requiring immediate attention

**For each insight provide:**
- type: one of pattern, anomaly, recommendation, trend, alert
- severity: one of critical, high, warning, medium, low, info
- title: concise title (max 60 chars)
- description: detailed explanation (2-3 sentences)
- suggested_action: what the user should do
- action_type: one of create_policy, investigate, review_duplicate, capacity_planning, optimize, schedule_maintenance
- confidence: float 0.0-1.0

**Output valid JSON array of insight objects. Return 3-8 insights.**
"""


class InsightsService(GeminiService):
    """
    AI-powered insights generation.
    Uses Gemini for real analysis, falls back to heuristic when unavailable.
    """

    async def generate(
        self,
        batch_id: Optional[str] = None,
        date_range_start: Optional[datetime] = None,
        date_range_end: Optional[datetime] = None,
        records: Optional[List[dict]] = None,
    ) -> InsightsListResponse:
        """
        Generate AI insights from data.

        Args:
            batch_id: Filter records by batch
            date_range_start: Start of date range
            date_range_end: End of date range
            records: Optional pre-fetched records to analyze
        """
        start_time = time.time()
        now = datetime.now(timezone.utc)

        if self.client and records and len(records) > 0:
            try:
                return await self._analyze_with_ai(records, now, start_time)
            except Exception as e:
                logger.warning(f"AI analysis failed, using heuristic: {e}")

        # Heuristic fallback
        insights = self._generate_heuristic_insights(now, records)
        patterns = self._generate_heuristic_patterns(records)
        actions = self._generate_heuristic_actions(insights)

        return InsightsListResponse(
            insights=insights,
            patterns=[p.model_dump() for p in patterns],
            actions=[a.model_dump() for a in actions],
            total_count=len(insights),
            generated_at=now,
            analysis_duration_ms=(time.time() - start_time) * 1000
        )

    async def _analyze_with_ai(
        self,
        records: List[dict],
        now: datetime,
        start_time: float,
    ) -> InsightsListResponse:
        """Run actual Gemini analysis on data records."""
        # Summarize records for the prompt (limit to avoid token overflow)
        sample = records[:50]
        data_summary = json.dumps(sample, indent=2, default=str)

        contents = [
            genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=f"Analyze this dataset and generate insights:\n\n{data_summary}")]
            )
        ]

        # Insights benefit from real reasoning — keep thinking_level=medium
        # (or whatever the env default is). Gemini 3 default temperature
        # (1.0) is recommended; do not set temperature explicitly.
        config = self._get_json_config(
            system_instruction=INSIGHTS_SYSTEM_PROMPT,
            thinking_level=None,  # use env default
        )

        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

        raw = json.loads(response.text.strip())
        if isinstance(raw, dict) and "insights" in raw:
            raw = raw["insights"]

        insights = []
        for i, item in enumerate(raw):
            insights.append(InsightResponse(
                id=f"ai-insight-{now.strftime('%Y%m%d%H%M')}-{i+1:03d}",
                type=item.get("type", "recommendation"),
                severity=item.get("severity", "info"),
                title=item.get("title", "Untitled Insight"),
                description=item.get("description", ""),
                data=item.get("data"),
                suggested_action=item.get("suggested_action"),
                action_type=item.get("action_type"),
                confidence=float(item.get("confidence", 0.7)),
                created_at=now,
                is_dismissed=False,
                is_actioned=False,
            ))

        return InsightsListResponse(
            insights=insights,
            patterns=[],
            actions=[],
            total_count=len(insights),
            generated_at=now,
            analysis_duration_ms=(time.time() - start_time) * 1000,
        )

    def _generate_heuristic_insights(self, now: datetime, records: Optional[List[dict]] = None) -> list:
        """Generate insights using heuristic rules when AI is unavailable."""
        insights = []

        if not records:
            return [
                InsightResponse(
                    id="heuristic-001",
                    type=InsightType.RECOMMENDATION,
                    severity=InsightSeverity.INFO,
                    title="No Data Available for Analysis",
                    description="No records were provided for analysis. Connect a data source or run the demo seed to populate sample data.",
                    suggested_action="Seed demo data or connect a data source",
                    action_type="configure",
                    confidence=1.0,
                    created_at=now,
                )
            ]

        record_count = len(records)

        # Basic statistical analysis
        if record_count > 10:
            insights.append(InsightResponse(
                id="heuristic-volume-001",
                type=InsightType.PATTERN,
                severity=InsightSeverity.INFO,
                title=f"Dataset Contains {record_count} Records",
                description=f"Analysis performed on {record_count} records. Consider using AI analysis for deeper pattern detection.",
                data={"record_count": record_count},
                confidence=1.0,
                created_at=now,
            ))

        return insights

    def _generate_heuristic_patterns(self, records: Optional[List[dict]] = None) -> list:
        """Generate patterns using heuristic analysis."""
        if not records or len(records) < 5:
            return []
        return [
            PatternInfo(
                name="Data Volume",
                frequency="ongoing",
                confidence=1.0,
                sample_size=len(records),
                description=f"Active dataset with {len(records)} records",
            )
        ]

    def _generate_heuristic_actions(self, insights: list) -> list:
        """Generate action recommendations based on insights."""
        actions = []
        for insight in insights:
            if hasattr(insight, 'action_type') and insight.action_type:
                actions.append(ActionRecommendation(
                    title=insight.suggested_action or "Review this insight",
                    priority="medium",
                    estimated_impact="Requires investigation",
                    action_type=insight.action_type,
                ))
        return actions


# Singleton instance
insights_service = InsightsService()

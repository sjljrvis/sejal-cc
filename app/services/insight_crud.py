"""
Insight CRUD Service - Database operations for AI insights.

Pure CRUD layer — no business logic. AI analysis lives in InsightsService.
"""

import logging
from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.insight import Insight

logger = logging.getLogger(__name__)


class InsightCRUD:
    """Database CRUD operations for insights."""

    def create(self, db: Session, *, data: dict) -> Insight:
        """Create a new insight."""
        insight = Insight(
            id=data.get("id"),
            type=data["type"],
            severity=data["severity"],
            title=data["title"],
            description=data["description"],
            data=data.get("data"),
            suggested_action=data.get("suggested_action"),
            action_type=data.get("action_type"),
            confidence=data.get("confidence", 0.8),
            source=data.get("source", "ai"),
            batch_id=data.get("batch_id"),
            is_dismissed=data.get("is_dismissed", False),
            is_actioned=data.get("is_actioned", False),
        )
        if data.get("created_at"):
            insight.created_at = data["created_at"]

        db.add(insight)
        db.commit()
        db.refresh(insight)
        return insight

    def bulk_create(self, db: Session, *, items: List[dict]) -> int:
        """Create multiple insights in one transaction. Returns count created."""
        count = 0
        for data in items:
            insight = Insight(
                id=data.get("id"),
                type=data["type"],
                severity=data["severity"],
                title=data["title"],
                description=data["description"],
                data=data.get("data"),
                suggested_action=data.get("suggested_action"),
                action_type=data.get("action_type"),
                confidence=data.get("confidence", 0.8),
                source=data.get("source", "ai"),
                batch_id=data.get("batch_id"),
                is_dismissed=data.get("is_dismissed", False),
                is_actioned=data.get("is_actioned", False),
            )
            if data.get("created_at"):
                insight.created_at = data["created_at"]
            db.add(insight)
            count += 1
        db.commit()
        return count

    def get(self, db: Session, insight_id: str) -> Optional[Insight]:
        return db.query(Insight).filter(Insight.id == insight_id).first()

    def list(
        self,
        db: Session,
        *,
        type: Optional[str] = None,
        severity: Optional[str] = None,
        source: Optional[str] = None,
        batch_id: Optional[str] = None,
        include_dismissed: bool = False,
    ) -> List[Insight]:
        query = db.query(Insight)

        if not include_dismissed:
            query = query.filter(Insight.is_dismissed == False)

        if type:
            query = query.filter(Insight.type == type)
        if severity:
            query = query.filter(Insight.severity == severity)
        if source:
            query = query.filter(Insight.source == source)
        if batch_id:
            query = query.filter(Insight.batch_id == batch_id)

        return query.order_by(Insight.created_at.desc()).all()

    def dismiss(self, db: Session, insight_id: str, *, user_id: Optional[str] = None) -> Optional[Insight]:
        """Mark an insight as dismissed."""
        insight = self.get(db, insight_id)
        if not insight:
            return None
        insight.is_dismissed = True
        insight.dismissed_by = user_id
        insight.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(insight)
        return insight

    def mark_actioned(self, db: Session, insight_id: str, *, user_id: Optional[str] = None) -> Optional[Insight]:
        """Mark an insight as actioned."""
        insight = self.get(db, insight_id)
        if not insight:
            return None
        insight.is_actioned = True
        insight.actioned_by = user_id
        insight.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(insight)
        return insight

    def delete_by_source(self, db: Session, source: str) -> int:
        """Delete all insights with a given source. Returns count deleted."""
        count = db.query(Insight).filter(Insight.source == source).delete()
        db.commit()
        return count

    def count(self, db: Session, *, include_dismissed: bool = False) -> int:
        query = db.query(Insight)
        if not include_dismissed:
            query = query.filter(Insight.is_dismissed == False)
        return query.count()


insight_crud = InsightCRUD()

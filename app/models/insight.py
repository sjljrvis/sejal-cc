"""
AI Insight Model - Persistent storage for AI-generated insights.

Insights represent AI-discovered patterns, anomalies, recommendations,
trends, and alerts derived from data analysis.
"""

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, String, Text, func
import uuid

from ..core.database import Base


class Insight(Base):
    """Persistent AI insight record."""

    __tablename__ = "insights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # Classification
    type = Column(String(20), nullable=False, index=True)       # pattern, anomaly, recommendation, trend, alert
    severity = Column(String(20), nullable=False, index=True)   # critical, high, warning, medium, low, info

    # Content
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)

    # Actionability
    suggested_action = Column(String(500), nullable=True)
    action_type = Column(String(50), nullable=True, index=True)  # create_policy, investigate, review_duplicate, etc.
    confidence = Column(Float, nullable=False, default=0.8)

    # Provenance
    source = Column(String(20), nullable=False, default="ai", index=True)  # ai, demo, user
    batch_id = Column(String(100), nullable=True, index=True)

    # User interaction state
    is_dismissed = Column(Boolean, nullable=False, default=False)
    is_actioned = Column(Boolean, nullable=False, default=False)
    dismissed_by = Column(String(255), nullable=True)
    actioned_by = Column(String(255), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Insight {self.id}: {self.title[:40]} ({self.type}/{self.severity})>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "data": self.data,
            "suggested_action": self.suggested_action,
            "action_type": self.action_type,
            "confidence": self.confidence,
            "source": self.source,
            "batch_id": self.batch_id,
            "is_dismissed": self.is_dismissed,
            "is_actioned": self.is_actioned,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

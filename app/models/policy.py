# app/models/policy.py
"""
AI Policy Model - Persistent storage for AI policies.

Policies define business rules in two formats:
- LOGICAL: Structured DSL with conditions and actions (evaluated by RuleEngine)
- NATURAL_LANGUAGE: AI-refined instructions (interpreted by Gemini)

Policy scope determines hierarchy:
- BASE: System-wide default rules
- INSTRUCTION: Entity-specific overrides (higher priority than BASE)
- CUSTOM: User-defined custom rules
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from ..core.database import Base


class PolicyScope:
    """Policy hierarchy scope."""
    BASE = "base"              # System-wide rules
    INSTRUCTION = "instruction" # Entity-specific overrides
    CUSTOM = "custom"          # User-defined rules


class Policy(Base):
    """
    AI Policy - persistent rule definition.

    Supports two execution types (policy_type):
    - logical: Structured DSL with conditions/actions evaluated by RuleEngine
    - natural_language: AI-refined instruction interpreted by Gemini

    And three hierarchy scopes (policy_scope):
    - base: System-wide defaults
    - instruction: Entity-specific overrides
    - custom: User-defined rules

    Separation of concerns:
    - policy_type = HOW the rule is processed
    - policy_scope = WHERE in the hierarchy it sits
    """

    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # Core fields
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True, default="")
    summary = Column(String(200), nullable=True)

    # Original user input - always preserved
    original_input = Column(Text, nullable=False)

    # Execution type: how the AI processes this policy
    policy_type = Column(String(20), nullable=False, default="natural_language", index=True)

    # Hierarchy scope: where this rule sits in the priority chain
    policy_scope = Column(String(20), nullable=False, default="base", index=True)

    # For LOGICAL type - structured DSL stored as JSON
    dsl = Column(JSON, nullable=True)

    # For NATURAL_LANGUAGE type - AI-refined instruction
    refined_instruction = Column(Text, nullable=True)

    # The computed instruction the AI engine uses (derived from DSL or refined_instruction)
    ai_instruction = Column(Text, nullable=True)

    # Entity this policy applies to (for INSTRUCTION scope)
    entity_name = Column(String(200), nullable=True, index=True)

    # Status and priority
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    priority = Column(Integer, nullable=False, default=100)

    # Tags stored as JSON array
    tags = Column(JSON, nullable=False, default=list)

    # Data source: 'user' or 'demo'
    source = Column(String(20), nullable=False, default="user", index=True)

    # Execution tracking
    execution_count = Column(Integer, nullable=False, default=0)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"<Policy {self.id}: {self.name} ({self.policy_type}/{self.policy_scope})>"

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses and rule compilation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description or "",
            "summary": self.summary,
            "natural_language": self.original_input,
            "original_input": self.original_input,
            "policy_type": self.policy_type,
            "policy_scope": self.policy_scope,
            "dsl": self.dsl,
            "refined_instruction": self.refined_instruction,
            "ai_instruction": self.ai_instruction,
            "entity_name": self.entity_name,
            "is_active": self.is_active,
            "priority": self.priority,
            "tags": self.tags or [],
            "source": self.source,
            "execution_count": self.execution_count,
            "last_executed_at": self.last_executed_at.isoformat() if self.last_executed_at else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

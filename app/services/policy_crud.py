"""
Policy CRUD Service - Database operations for AI policies.

Provides all CRUD operations for the policies table.
Business logic (AI analysis, conflict detection) belongs in the router or PolicyService.
"""

import logging
from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.policy import Policy

logger = logging.getLogger(__name__)


class PolicyCRUD:
    """Database CRUD operations for policies."""

    def create(self, db: Session, *, data: dict, created_by: Optional[str] = None) -> Policy:
        """Create a new policy."""
        policy = Policy(
            id=data.get("id"),
            name=data["name"],
            description=data.get("description", ""),
            summary=data.get("summary"),
            original_input=data["original_input"],
            policy_type=data.get("policy_type", "natural_language"),
            policy_scope=data.get("policy_scope", "base"),
            dsl=data.get("dsl"),
            refined_instruction=data.get("refined_instruction"),
            ai_instruction=data.get("ai_instruction"),
            entity_name=data.get("entity_name"),
            is_active=data.get("is_active", True),
            priority=data.get("priority", 100),
            tags=data.get("tags", []),
            source=data.get("source", "user"),
            execution_count=data.get("execution_count", 0),
            last_executed_at=data.get("last_executed_at"),
            created_by=created_by,
        )
        # Allow explicit created_at for demo seeding
        if data.get("created_at"):
            policy.created_at = data["created_at"]
        if data.get("updated_at"):
            policy.updated_at = data["updated_at"]

        db.add(policy)
        db.commit()
        db.refresh(policy)
        return policy

    def get(self, db: Session, policy_id: str) -> Optional[Policy]:
        """Get a single policy by ID."""
        return db.query(Policy).filter(Policy.id == policy_id).first()

    def list(
        self,
        db: Session,
        *,
        is_active: Optional[bool] = None,
        policy_type: Optional[str] = None,
        policy_scope: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Policy]:
        """List policies with optional filters."""
        query = db.query(Policy)

        if is_active is not None:
            query = query.filter(Policy.is_active == is_active)

        if policy_type:
            query = query.filter(Policy.policy_type == policy_type)

        if policy_scope:
            query = query.filter(Policy.policy_scope == policy_scope)

        if source:
            query = query.filter(Policy.source == source)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Policy.name.ilike(search_term),
                    Policy.original_input.ilike(search_term),
                    Policy.description.ilike(search_term),
                )
            )

        return query.order_by(Policy.priority.asc(), Policy.created_at.desc()).all()

    def list_active(self, db: Session) -> List[Policy]:
        """List all active policies, ordered by priority."""
        return (
            db.query(Policy)
            .filter(Policy.is_active == True)
            .order_by(Policy.priority.asc())
            .all()
        )

    def update(self, db: Session, policy_id: str, *, data: dict) -> Optional[Policy]:
        """Update a policy. Returns None if not found."""
        policy = self.get(db, policy_id)
        if not policy:
            return None

        for key, value in data.items():
            if hasattr(policy, key) and key not in ("id", "created_at", "created_by"):
                setattr(policy, key, value)

        policy.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(policy)
        return policy

    def delete(self, db: Session, policy_id: str) -> bool:
        """Delete a policy. Returns True if deleted."""
        policy = self.get(db, policy_id)
        if not policy:
            return False

        db.delete(policy)
        db.commit()
        return True

    def count(self, db: Session, *, is_active: Optional[bool] = None) -> int:
        """Count policies."""
        query = db.query(Policy)
        if is_active is not None:
            query = query.filter(Policy.is_active == is_active)
        return query.count()

    def delete_by_source(self, db: Session, source: str) -> int:
        """Delete all policies with a given source. Returns count deleted."""
        count = db.query(Policy).filter(Policy.source == source).delete()
        db.commit()
        return count

    def increment_execution(self, db: Session, policy_id: str) -> None:
        """Increment the execution count for a policy."""
        policy = self.get(db, policy_id)
        if policy:
            policy.execution_count = (policy.execution_count or 0) + 1
            policy.last_executed_at = datetime.now(timezone.utc)
            db.commit()


# Singleton
policy_crud = PolicyCRUD()

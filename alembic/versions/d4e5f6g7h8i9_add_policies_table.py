"""Add policies table

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2026-05-05 11:00:00.000000

Creates the policies table for persistent AI policy storage.
Replaces the in-memory _policies_store dict.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6g7h8i9'
down_revision = 'c3d4e5f6g7h8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'policies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True, server_default=''),
        sa.Column('summary', sa.String(200), nullable=True),
        sa.Column('original_input', sa.Text(), nullable=False),
        sa.Column('policy_type', sa.String(20), nullable=False, server_default='natural_language'),
        sa.Column('policy_scope', sa.String(20), nullable=False, server_default='base'),
        sa.Column('dsl', sa.JSON(), nullable=True),
        sa.Column('refined_instruction', sa.Text(), nullable=True),
        sa.Column('ai_instruction', sa.Text(), nullable=True),
        sa.Column('entity_name', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('source', sa.String(20), nullable=False, server_default='user'),
        sa.Column('execution_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Indexes for common query patterns
    op.create_index('ix_policies_id', 'policies', ['id'])
    op.create_index('ix_policies_policy_type', 'policies', ['policy_type'])
    op.create_index('ix_policies_policy_scope', 'policies', ['policy_scope'])
    op.create_index('ix_policies_is_active', 'policies', ['is_active'])
    op.create_index('ix_policies_entity_name', 'policies', ['entity_name'])
    op.create_index('ix_policies_source', 'policies', ['source'])
    op.create_index('ix_policies_created_at', 'policies', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_policies_created_at', table_name='policies')
    op.drop_index('ix_policies_source', table_name='policies')
    op.drop_index('ix_policies_entity_name', table_name='policies')
    op.drop_index('ix_policies_is_active', table_name='policies')
    op.drop_index('ix_policies_policy_scope', table_name='policies')
    op.drop_index('ix_policies_policy_type', table_name='policies')
    op.drop_index('ix_policies_id', table_name='policies')
    op.drop_table('policies')

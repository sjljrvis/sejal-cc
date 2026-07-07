"""Add insights table

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-05-05 11:30:00.000000

Creates the insights table for persistent AI insight storage.
"""

from alembic import op
import sqlalchemy as sa

revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'insights',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('suggested_action', sa.String(500), nullable=True),
        sa.Column('action_type', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.8'),
        sa.Column('source', sa.String(20), nullable=False, server_default='ai'),
        sa.Column('batch_id', sa.String(100), nullable=True),
        sa.Column('is_dismissed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_actioned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('dismissed_by', sa.String(255), nullable=True),
        sa.Column('actioned_by', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index('ix_insights_id', 'insights', ['id'])
    op.create_index('ix_insights_type', 'insights', ['type'])
    op.create_index('ix_insights_severity', 'insights', ['severity'])
    op.create_index('ix_insights_action_type', 'insights', ['action_type'])
    op.create_index('ix_insights_source', 'insights', ['source'])
    op.create_index('ix_insights_batch_id', 'insights', ['batch_id'])
    op.create_index('ix_insights_created_at', 'insights', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_insights_created_at', table_name='insights')
    op.drop_index('ix_insights_batch_id', table_name='insights')
    op.drop_index('ix_insights_source', table_name='insights')
    op.drop_index('ix_insights_action_type', table_name='insights')
    op.drop_index('ix_insights_severity', table_name='insights')
    op.drop_index('ix_insights_type', table_name='insights')
    op.drop_index('ix_insights_id', table_name='insights')
    op.drop_table('insights')

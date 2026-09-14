"""add service hooks

Revision ID: f2c8a19b6043
Revises: d9a3c5f1e742
Create Date: 2026-09-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "f2c8a19b6043"
down_revision = "d9a3c5f1e742"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "service_hooks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("event_name", sa.String(length=80), nullable=False),
        sa.Column("handler_key", sa.String(length=180), nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("execution_order", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("service_id", "event_name", "handler_key", name="uq_service_hook_handler"),
    )
    op.create_index("ix_service_hooks_event", "service_hooks", ["service_id", "event_name"], unique=False)

    op.create_table(
        "service_hook_executions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hook_id", sa.Integer(), nullable=False),
        sa.Column("service_request_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("event_name", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("messages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("warnings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["hook_id"], ["service_hooks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_request_id"], ["service_requests.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_service_hook_executions_request",
        "service_hook_executions",
        ["service_request_id"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_service_hook_executions_request", table_name="service_hook_executions")
    op.drop_table("service_hook_executions")
    op.drop_index("ix_service_hooks_event", table_name="service_hooks")
    op.drop_table("service_hooks")

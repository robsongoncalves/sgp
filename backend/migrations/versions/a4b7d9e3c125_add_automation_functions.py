"""add automation functions

Revision ID: a4b7d9e3c125
Revises: f2c8a19b6043
Create Date: 2026-09-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "a4b7d9e3c125"
down_revision = "f2c8a19b6043"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("uq_service_hook_handler", "service_hooks", type_="unique")
    op.create_table(
        "automation_functions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=40), nullable=False),
        sa.Column("source_code", sa.Text(), nullable=False),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_automation_functions_slug", "automation_functions", ["slug"], unique=False)
    op.add_column("service_hooks", sa.Column("function_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_service_hooks_function_id",
        "service_hooks",
        "automation_functions",
        ["function_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint("fk_service_hooks_function_id", "service_hooks", type_="foreignkey")
    op.drop_column("service_hooks", "function_id")
    op.drop_index("ix_automation_functions_slug", table_name="automation_functions")
    op.drop_table("automation_functions")
    op.create_unique_constraint(
        "uq_service_hook_handler",
        "service_hooks",
        ["service_id", "event_name", "handler_key"],
    )

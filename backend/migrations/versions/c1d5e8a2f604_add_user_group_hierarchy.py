"""add user group hierarchy

Revision ID: c1d5e8a2f604
Revises: b9f4a2c7d801
Create Date: 2026-09-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c1d5e8a2f604"
down_revision = "b9f4a2c7d801"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user_groups", sa.Column("parent_group_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_user_groups_parent_group_id",
        "user_groups",
        "user_groups",
        ["parent_group_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint("fk_user_groups_parent_group_id", "user_groups", type_="foreignkey")
    op.drop_column("user_groups", "parent_group_id")

"""add user group manager

Revision ID: e8c2a41f7d33
Revises: d4f6a2b8c901
Create Date: 2026-09-11 16:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e8c2a41f7d33"
down_revision = "d4f6a2b8c901"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user_groups", schema=None) as batch_op:
        batch_op.add_column(sa.Column("manager_user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_user_groups_manager_user_id_users",
            "users",
            ["manager_user_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade():
    with op.batch_alter_table("user_groups", schema=None) as batch_op:
        batch_op.drop_constraint("fk_user_groups_manager_user_id_users", type_="foreignkey")
        batch_op.drop_column("manager_user_id")

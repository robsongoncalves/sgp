"""add service category hierarchy

Revision ID: d2f6a4b8c913
Revises: c1d5e8a2f604
Create Date: 2026-09-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d2f6a4b8c913"
down_revision = "c1d5e8a2f604"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("service_categories", sa.Column("parent_category_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_service_categories_parent_category_id",
        "service_categories",
        "service_categories",
        ["parent_category_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint(
        "fk_service_categories_parent_category_id",
        "service_categories",
        type_="foreignkey",
    )
    op.drop_column("service_categories", "parent_category_id")

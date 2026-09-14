"""add service category main menu flag

Revision ID: e3a9c7d1f482
Revises: d2f6a4b8c913
Create Date: 2026-09-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "e3a9c7d1f482"
down_revision = "d2f6a4b8c913"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "service_categories",
        sa.Column("show_on_main_menu", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("service_categories", "show_on_main_menu", server_default=None)


def downgrade():
    op.drop_column("service_categories", "show_on_main_menu")

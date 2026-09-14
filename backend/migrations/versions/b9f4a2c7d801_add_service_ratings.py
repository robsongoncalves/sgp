"""add service ratings

Revision ID: b9f4a2c7d801
Revises: a4b7d9e3c125
Create Date: 2026-09-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b9f4a2c7d801"
down_revision = "a4b7d9e3c125"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "service_ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("service_id", "user_id", name="uq_service_rating_user"),
    )


def downgrade():
    op.drop_table("service_ratings")

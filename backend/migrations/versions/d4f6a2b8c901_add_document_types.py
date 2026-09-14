"""add document types

Revision ID: d4f6a2b8c901
Revises: c8a71d4e9b02
Create Date: 2026-09-11 14:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d4f6a2b8c901"
down_revision = "c8a71d4e9b02"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "document_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("origin", sa.String(length=40), nullable=False),
        sa.Column("allowed_formats", sa.String(length=180), nullable=False),
        sa.Column("required_by_default", sa.Boolean(), nullable=False),
        sa.Column("allow_multiple_files", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_document_types_code"), "document_types", ["code"], unique=False)
    op.create_table(
        "service_situation_document_type_association",
        sa.Column("situation_id", sa.Integer(), nullable=False),
        sa.Column("document_type_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["document_type_id"], ["document_types.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["situation_id"], ["service_situations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("situation_id", "document_type_id"),
    )


def downgrade():
    op.drop_table("service_situation_document_type_association")
    op.drop_index(op.f("ix_document_types_code"), table_name="document_types")
    op.drop_table("document_types")

"""add service request documents

Revision ID: a7d2e5f8c930
Revises: f1b3c9d7e204
Create Date: 2026-09-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "a7d2e5f8c930"
down_revision = "f1b3c9d7e204"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "service_request_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_request_id", sa.Integer(), nullable=False),
        sa.Column("service_situation_id", sa.Integer(), nullable=False),
        sa.Column("document_type_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("content_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_type_id"], ["document_types.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["service_request_id"], ["service_requests.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_situation_id"], ["service_situations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_service_request_documents_request",
        "service_request_documents",
        ["service_request_id"],
        unique=False,
    )

    op.add_column(
        "service_request_attachments",
        sa.Column("service_request_document_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_service_request_attachments_document_id",
        "service_request_attachments",
        "service_request_documents",
        ["service_request_document_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint(
        "fk_service_request_attachments_document_id",
        "service_request_attachments",
        type_="foreignkey",
    )
    op.drop_column("service_request_attachments", "service_request_document_id")
    op.drop_index("ix_service_request_documents_request", table_name="service_request_documents")
    op.drop_table("service_request_documents")

"""add linked service documents

Revision ID: d9a3c5f1e742
Revises: b8e4f1a2d650
Create Date: 2026-09-14 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d9a3c5f1e742"
down_revision = "b8e4f1a2d650"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("document_types", sa.Column("linked_service_id", sa.Integer(), nullable=True))
    op.add_column(
        "document_types",
        sa.Column("linked_service_required_status", sa.String(length=120), nullable=False, server_default=""),
    )
    op.add_column("service_request_documents", sa.Column("linked_service_request_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_document_types_linked_service_id",
        "document_types",
        "services",
        ["linked_service_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_service_request_documents_linked_service_request_id",
        "service_request_documents",
        "service_requests",
        ["linked_service_request_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_service_request_documents_linked_request",
        "service_request_documents",
        ["linked_service_request_id"],
        unique=False,
    )
    op.alter_column("document_types", "linked_service_required_status", server_default=None)


def downgrade():
    op.drop_index("ix_service_request_documents_linked_request", table_name="service_request_documents")
    op.drop_constraint(
        "fk_service_request_documents_linked_service_request_id",
        "service_request_documents",
        type_="foreignkey",
    )
    op.drop_constraint("fk_document_types_linked_service_id", "document_types", type_="foreignkey")
    op.drop_column("service_request_documents", "linked_service_request_id")
    op.drop_column("document_types", "linked_service_required_status")
    op.drop_column("document_types", "linked_service_id")

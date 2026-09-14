"""add document assignment decision

Revision ID: b8e4f1a2d650
Revises: a7d2e5f8c930
Create Date: 2026-09-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b8e4f1a2d650"
down_revision = "a7d2e5f8c930"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("service_request_documents", sa.Column("assigned_to_user_id", sa.Integer(), nullable=True))
    op.add_column("service_request_documents", sa.Column("assigned_to_group_id", sa.Integer(), nullable=True))
    op.add_column("service_request_documents", sa.Column("decided_by_user_id", sa.Integer(), nullable=True))
    op.add_column("service_request_documents", sa.Column("decided_at", sa.DateTime(), nullable=True))
    op.add_column(
        "service_request_documents",
        sa.Column("decision", sa.String(length=40), nullable=False, server_default=""),
    )
    op.add_column(
        "service_request_documents",
        sa.Column("decision_text", sa.Text(), nullable=False, server_default=""),
    )
    op.create_foreign_key(
        "fk_service_request_documents_assigned_user_id",
        "service_request_documents",
        "users",
        ["assigned_to_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_service_request_documents_assigned_group_id",
        "service_request_documents",
        "user_groups",
        ["assigned_to_group_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_service_request_documents_decided_user_id",
        "service_request_documents",
        "users",
        ["decided_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_service_request_documents_assigned_user",
        "service_request_documents",
        ["assigned_to_user_id"],
        unique=False,
    )
    op.alter_column("service_request_documents", "decision", server_default=None)
    op.alter_column("service_request_documents", "decision_text", server_default=None)


def downgrade():
    op.drop_index("ix_service_request_documents_assigned_user", table_name="service_request_documents")
    op.drop_constraint("fk_service_request_documents_decided_user_id", "service_request_documents", type_="foreignkey")
    op.drop_constraint("fk_service_request_documents_assigned_group_id", "service_request_documents", type_="foreignkey")
    op.drop_constraint("fk_service_request_documents_assigned_user_id", "service_request_documents", type_="foreignkey")
    op.drop_column("service_request_documents", "decision_text")
    op.drop_column("service_request_documents", "decision")
    op.drop_column("service_request_documents", "decided_at")
    op.drop_column("service_request_documents", "decided_by_user_id")
    op.drop_column("service_request_documents", "assigned_to_group_id")
    op.drop_column("service_request_documents", "assigned_to_user_id")

"""add form and opinion templates

Revision ID: f1b3c9d7e204
Revises: e8c2a41f7d33
Create Date: 2026-09-11 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "f1b3c9d7e204"
down_revision = "e8c2a41f7d33"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "form_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("execution_mode", sa.String(length=40), nullable=False),
        sa.Column("fields_schema", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_form_templates_slug"), "form_templates", ["slug"], unique=False)

    op.create_table(
        "opinion_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("execution_mode", sa.String(length=40), nullable=False),
        sa.Column("default_responsible_group_id", sa.Integer(), nullable=True),
        sa.Column("decision_options", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("fields_schema", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("requires_justification", sa.Boolean(), nullable=False),
        sa.Column("requires_signature", sa.Boolean(), nullable=False),
        sa.Column("allow_attachments", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["default_responsible_group_id"], ["user_groups.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_opinion_templates_slug"), "opinion_templates", ["slug"], unique=False)

    op.add_column(
        "document_types",
        sa.Column("purpose", sa.String(length=40), nullable=False, server_default="attachment"),
    )
    op.add_column(
        "document_types",
        sa.Column("module_slug", sa.String(length=120), nullable=False, server_default=""),
    )
    op.add_column("document_types", sa.Column("form_template_id", sa.Integer(), nullable=True))
    op.add_column("document_types", sa.Column("opinion_template_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_document_types_form_template_id",
        "document_types",
        "form_templates",
        ["form_template_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_document_types_opinion_template_id",
        "document_types",
        "opinion_templates",
        ["opinion_template_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade():
    op.drop_constraint("fk_document_types_opinion_template_id", "document_types", type_="foreignkey")
    op.drop_constraint("fk_document_types_form_template_id", "document_types", type_="foreignkey")
    op.drop_column("document_types", "opinion_template_id")
    op.drop_column("document_types", "form_template_id")
    op.drop_column("document_types", "module_slug")
    op.drop_column("document_types", "purpose")

    op.drop_index(op.f("ix_opinion_templates_slug"), table_name="opinion_templates")
    op.drop_table("opinion_templates")

    op.drop_index(op.f("ix_form_templates_slug"), table_name="form_templates")
    op.drop_table("form_templates")

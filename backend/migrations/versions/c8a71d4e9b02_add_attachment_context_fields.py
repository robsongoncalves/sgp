"""add attachment context fields

Revision ID: c8a71d4e9b02
Revises: 9f2b7a6c4d1e
Create Date: 2026-09-08 11:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c8a71d4e9b02"
down_revision = "9f2b7a6c4d1e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("service_request_attachments", schema=None) as batch_op:
        batch_op.add_column(sa.Column("context_type", sa.String(length=80), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("requirement_code", sa.String(length=20), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("item_index", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("description", sa.Text(), nullable=False, server_default=""))

    with op.batch_alter_table("service_request_attachments", schema=None) as batch_op:
        batch_op.alter_column("context_type", server_default=None)
        batch_op.alter_column("requirement_code", server_default=None)
        batch_op.alter_column("description", server_default=None)


def downgrade():
    with op.batch_alter_table("service_request_attachments", schema=None) as batch_op:
        batch_op.drop_column("description")
        batch_op.drop_column("item_index")
        batch_op.drop_column("requirement_code")
        batch_op.drop_column("context_type")

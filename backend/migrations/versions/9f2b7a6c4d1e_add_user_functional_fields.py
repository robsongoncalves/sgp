"""add user functional fields

Revision ID: 9f2b7a6c4d1e
Revises: 715e6e2489b2
Create Date: 2026-09-08 10:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "9f2b7a6c4d1e"
down_revision = "715e6e2489b2"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("siape", sa.String(length=20), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("cargo", sa.String(length=140), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("classe_nivel", sa.String(length=80), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("local_exercicio", sa.String(length=180), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("telefone", sa.String(length=40), nullable=False, server_default=""))

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column("siape", server_default=None)
        batch_op.alter_column("cargo", server_default=None)
        batch_op.alter_column("classe_nivel", server_default=None)
        batch_op.alter_column("local_exercicio", server_default=None)
        batch_op.alter_column("telefone", server_default=None)


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("telefone")
        batch_op.drop_column("local_exercicio")
        batch_op.drop_column("classe_nivel")
        batch_op.drop_column("cargo")
        batch_op.drop_column("siape")

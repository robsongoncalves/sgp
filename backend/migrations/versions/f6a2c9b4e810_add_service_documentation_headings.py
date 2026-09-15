"""Persist documentation import headings per service."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'f6a2c9b4e810'
down_revision = 'e3a9c7d1f482'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('services', sa.Column(
        'documentation_headings', postgresql.JSONB(), nullable=False,
        server_default=sa.text("'[\"DEFINIÇÃO\", \"QUEM FAZ?\"]'::jsonb"),
    ))
    op.alter_column('services', 'documentation_headings', server_default=None)


def downgrade():
    op.drop_column('services', 'documentation_headings')

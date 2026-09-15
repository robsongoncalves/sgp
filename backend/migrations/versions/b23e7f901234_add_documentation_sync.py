"""Opt-in synchronization for documentations."""
from alembic import op
import sqlalchemy as sa

revision = 'b23e7f901234'
down_revision = 'a12d6e8f9012'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('documentations', sa.Column('sync_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column('documentations', 'sync_enabled')

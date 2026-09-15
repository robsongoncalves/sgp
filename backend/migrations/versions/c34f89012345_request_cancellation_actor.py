"""Record the user responsible for request cancellation."""
from alembic import op
import sqlalchemy as sa

revision = 'c34f89012345'
down_revision = 'b23e7f901234'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('service_requests', sa.Column('canceled_by_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_request_canceled_by', 'service_requests', 'users', ['canceled_by_user_id'], ['id'], ondelete='RESTRICT')


def downgrade():
    op.drop_constraint('fk_request_canceled_by', 'service_requests', type_='foreignkey')
    op.drop_column('service_requests', 'canceled_by_user_id')

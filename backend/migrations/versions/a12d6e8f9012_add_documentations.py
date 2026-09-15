"""Create reusable documentations and preserve existing service content."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'a12d6e8f9012'
down_revision = 'f6a2c9b4e810'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('documentations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('headings', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.add_column('services', sa.Column('documentation_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_services_documentation', 'services', 'documentations', ['documentation_id'], ['id'], ondelete='RESTRICT')
    op.create_index('ix_services_documentation_id', 'services', ['documentation_id'])
    # Keep distinct content even when two services share the same URL.
    op.execute("""
        INSERT INTO documentations (url, description, headings, created_at, updated_at)
        SELECT DISTINCT documentation_url, description, documentation_headings, NOW(), NOW()
        FROM services WHERE documentation_url <> '' OR description <> '';
        UPDATE services s SET documentation_id = d.id FROM documentations d
        WHERE s.documentation_url = d.url AND s.description = d.description
          AND s.documentation_headings = d.headings;
    """)


def downgrade():
    op.execute("""UPDATE services s SET documentation_url = d.url,
        description = d.description, documentation_headings = d.headings
        FROM documentations d WHERE s.documentation_id = d.id""")
    op.drop_index('ix_services_documentation_id', table_name='services')
    op.drop_constraint('fk_services_documentation', 'services', type_='foreignkey')
    op.drop_column('services', 'documentation_id')
    op.drop_table('documentations')

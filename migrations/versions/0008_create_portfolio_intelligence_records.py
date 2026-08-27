"""create portfolio_intelligence_records table

Revision ID: 0008_create_portfolio_intelligence_records
Revises: 0007_create_monitoring_locks_and_retries
Create Date: 2026-08-27 21:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0008_create_portfolio_intelligence_records'
down_revision = '0007_create_monitoring_locks_and_retries'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'portfolio_intelligence_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('query', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('portfolio_overview', sa.Text(), nullable=False),
        sa.Column('portfolio_risks', sa.JSON(), nullable=True),
        sa.Column('portfolio_opportunities', sa.JSON(), nullable=True),
        sa.Column('watchlist_priorities', sa.JSON(), nullable=True),
        sa.Column('recommended_research', sa.JSON(), nullable=True),
        sa.Column('portfolio_summary', sa.JSON(), nullable=False),
        sa.Column('user_context', sa.Text(), nullable=True),
        sa.Column('facts', sa.JSON(), nullable=False),
        sa.Column('sources', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_portfolio_intelligence_records_user_id'), 'portfolio_intelligence_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_portfolio_intelligence_records_created_at'), 'portfolio_intelligence_records', ['created_at'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_portfolio_intelligence_records_created_at'), table_name='portfolio_intelligence_records')
    op.drop_index(op.f('ix_portfolio_intelligence_records_user_id'), table_name='portfolio_intelligence_records')
    op.drop_table('portfolio_intelligence_records')

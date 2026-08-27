"""create research_records table

Revision ID: 0002_create_research_records
Revises: 0001_create_users_and_profiles
Create Date: 2026-08-27 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_create_research_records'
down_revision = '0001_create_users_and_profiles'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'research_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('facts', sa.JSON(), nullable=False),
        sa.Column('fundamentals', sa.Text(), nullable=True),
        sa.Column('valuation', sa.Text(), nullable=True),
        sa.Column('market_context', sa.Text(), nullable=True),
        sa.Column('risks', sa.JSON(), nullable=True),
        sa.Column('opportunities', sa.JSON(), nullable=True),
        sa.Column('user_context', sa.Text(), nullable=True),
        sa.Column('sources', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_research_records_user_id'), 'research_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_research_records_symbol'), 'research_records', ['symbol'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_research_records_symbol'), table_name='research_records')
    op.drop_index(op.f('ix_research_records_user_id'), table_name='research_records')
    op.drop_table('research_records')

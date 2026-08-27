"""create watchlist_items and portfolio_holdings tables

Revision ID: 0003_create_watchlist_and_portfolio
Revises: 0002_create_research_records
Create Date: 2026-08-27 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_create_watchlist_and_portfolio'
down_revision = '0002_create_research_records'
branch_labels = None
depends_on = None


def upgrade():
    # 1. watchlist_items
    op.create_table(
        'watchlist_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'symbol', name='uq_watchlist_user_symbol')
    )
    op.create_index(op.f('ix_watchlist_items_user_id'), 'watchlist_items', ['user_id'], unique=False)
    op.create_index(op.f('ix_watchlist_items_symbol'), 'watchlist_items', ['symbol'], unique=False)

    # 2. portfolio_holdings
    op.create_table(
        'portfolio_holdings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=18, scale=6), nullable=False),
        sa.Column('average_cost', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'symbol', name='uq_portfolio_user_symbol')
    )
    op.create_index(op.f('ix_portfolio_holdings_user_id'), 'portfolio_holdings', ['user_id'], unique=False)
    op.create_index(op.f('ix_portfolio_holdings_symbol'), 'portfolio_holdings', ['symbol'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_portfolio_holdings_symbol'), table_name='portfolio_holdings')
    op.drop_index(op.f('ix_portfolio_holdings_user_id'), table_name='portfolio_holdings')
    op.drop_table('portfolio_holdings')

    op.drop_index(op.f('ix_watchlist_items_symbol'), table_name='watchlist_items')
    op.drop_index(op.f('ix_watchlist_items_user_id'), table_name='watchlist_items')
    op.drop_table('watchlist_items')

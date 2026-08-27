"""create users and user_profiles tables

Revision ID: 0001_create_users_and_profiles
Revises: 
Create Date: 2026-08-27 18:57:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_users_and_profiles'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('investment_focus', sa.String(length=255), nullable=True),
        sa.Column('risk_preference', sa.String(length=50), nullable=True),
        sa.Column('investment_horizon', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_profiles_user_id'), 'user_profiles', ['user_id'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_user_profiles_user_id'), table_name='user_profiles')
    op.drop_table('user_profiles')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

"""create notification preferences and endpoints tables

Revision ID: 0006_create_notification_preferences_and_endpoints
Revises: 0005_create_monitoring_and_notifications
Create Date: 2026-08-27 21:22:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0006_create_notification_preferences_and_endpoints'
down_revision = '0005_create_monitoring_and_notifications'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create notification_preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('in_app_enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('webhook_enabled', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('minimum_severity', sa.String(length=20), nullable=False, server_default='info'),
        sa.Column('alert_types', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', name='uq_notification_preference_user_id')
    )
    op.create_index(op.f('ix_notification_preferences_user_id'), 'notification_preferences', ['user_id'], unique=True)

    # 2. Create notification_endpoints table
    op.create_table(
        'notification_endpoints',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False, server_default='webhook'),
        sa.Column('endpoint_url', sa.String(length=500), nullable=False),
        sa.Column('secret_key', sa.String(length=255), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_endpoints_user_id'), 'notification_endpoints', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notification_endpoints_user_id'), table_name='notification_endpoints')
    op.drop_table('notification_endpoints')

    op.drop_index(op.f('ix_notification_preferences_user_id'), table_name='notification_preferences')
    op.drop_table('notification_preferences')

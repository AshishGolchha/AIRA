"""create monitoring locks table and retry columns

Revision ID: 0007_create_monitoring_locks_and_retries
Revises: 0006_create_notification_preferences_and_endpoints
Create Date: 2026-08-27 21:32:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0007_create_monitoring_locks_and_retries'
down_revision = '0006_create_notification_preferences_and_endpoints'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create monitoring_locks table
    op.create_table(
        'monitoring_locks',
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('locked_at', sa.DateTime(), nullable=False),
        sa.Column('locked_by', sa.String(length=100), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('name')
    )

    # 2. Add notification statistics to alert_monitoring_runs
    op.add_column('alert_monitoring_runs', sa.Column('notifications_attempted', sa.Integer(), nullable=False, server_default=sa.text('0')))
    op.add_column('alert_monitoring_runs', sa.Column('notifications_succeeded', sa.Integer(), nullable=False, server_default=sa.text('0')))
    op.add_column('alert_monitoring_runs', sa.Column('notifications_failed', sa.Integer(), nullable=False, server_default=sa.text('0')))

    # 3. Add retry metadata to notification_deliveries
    op.add_column('notification_deliveries', sa.Column('attempt_count', sa.Integer(), nullable=False, server_default=sa.text('1')))
    op.add_column('notification_deliveries', sa.Column('is_retryable', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.add_column('notification_deliveries', sa.Column('next_retry_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('notification_deliveries', 'next_retry_at')
    op.drop_column('notification_deliveries', 'is_retryable')
    op.drop_column('notification_deliveries', 'attempt_count')

    op.drop_column('alert_monitoring_runs', 'notifications_failed')
    op.drop_column('alert_monitoring_runs', 'notifications_succeeded')
    op.drop_column('alert_monitoring_runs', 'notifications_attempted')

    op.drop_table('monitoring_locks')

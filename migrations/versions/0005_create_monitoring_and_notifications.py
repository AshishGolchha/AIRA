"""create monitoring and notifications tables and add alerts_enabled to users

Revision ID: 0005_create_monitoring_and_notifications
Revises: 0004_create_alerts
Create Date: 2026-08-27 21:14:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0005_create_monitoring_and_notifications'
down_revision = '0004_create_alerts'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add alerts_enabled to users table
    op.add_column('users', sa.Column('alerts_enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')))

    # 2. Create alert_monitoring_runs table
    op.create_table(
        'alert_monitoring_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='in_progress'),
        sa.Column('users_checked', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('users_succeeded', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('users_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('alerts_generated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_summary', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Create notification_deliveries table
    op.create_table(
        'notification_deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(length=50), nullable=False, server_default='in_app'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='delivered'),
        sa.Column('attempted_at', sa.DateTime(), nullable=False),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('alert_id', 'channel', name='uq_notification_alert_channel')
    )
    op.create_index(op.f('ix_notification_deliveries_alert_id'), 'notification_deliveries', ['alert_id'], unique=False)
    op.create_index(op.f('ix_notification_deliveries_user_id'), 'notification_deliveries', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notification_deliveries_user_id'), table_name='notification_deliveries')
    op.drop_index(op.f('ix_notification_deliveries_alert_id'), table_name='notification_deliveries')
    op.drop_table('notification_deliveries')

    op.drop_table('alert_monitoring_runs')

    op.drop_column('users', 'alerts_enabled')

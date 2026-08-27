from datetime import datetime, timezone
from typing import Any
from app.extensions import db
from app.models.base import TimestampMixin


class AlertMonitoringRun(TimestampMixin, db.Model):
    """Tracks batch alert monitoring execution statistics and outcomes."""

    __tablename__ = "alert_monitoring_runs"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False, default="running")  # "pending", "running", "completed", "partial_failure", "failed"
    users_checked = db.Column(db.Integer, nullable=False, default=0)
    users_succeeded = db.Column(db.Integer, nullable=False, default=0)
    users_failed = db.Column(db.Integer, nullable=False, default=0)
    alerts_generated = db.Column(db.Integer, nullable=False, default=0)
    notifications_attempted = db.Column(db.Integer, nullable=False, default=0)
    notifications_succeeded = db.Column(db.Integer, nullable=False, default=0)
    notifications_failed = db.Column(db.Integer, nullable=False, default=0)
    error_summary = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    def __init__(
        self,
        status: str = "running",
        users_checked: int = 0,
        users_succeeded: int = 0,
        users_failed: int = 0,
        alerts_generated: int = 0,
        notifications_attempted: int = 0,
        notifications_succeeded: int = 0,
        notifications_failed: int = 0,
        error_summary: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.status = status
        self.users_checked = users_checked
        self.users_succeeded = users_succeeded
        self.users_failed = users_failed
        self.alerts_generated = alerts_generated
        self.notifications_attempted = notifications_attempted
        self.notifications_succeeded = notifications_succeeded
        self.notifications_failed = notifications_failed
        self.error_summary = error_summary
        self.started_at = started_at or datetime.now(timezone.utc)
        self.completed_at = completed_at

    def to_dict(self) -> dict[str, Any]:
        """Safe dictionary representation of AlertMonitoringRun."""
        duration = None
        if self.started_at and self.completed_at:
            duration = round((self.completed_at - self.started_at).total_seconds(), 2)

        return {
            "id": self.id,
            "status": self.status,
            "users_checked": self.users_checked,
            "users_scanned": self.users_checked,
            "users_succeeded": self.users_succeeded,
            "users_failed": self.users_failed,
            "alerts_generated": self.alerts_generated,
            "notifications_attempted": self.notifications_attempted,
            "notifications_succeeded": self.notifications_succeeded,
            "notifications_failed": self.notifications_failed,
            "duration_seconds": duration,
            "error_summary": self.error_summary,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class MonitoringLock(TimestampMixin, db.Model):
    """Database-backed distributed concurrency lock for scheduled monitoring jobs."""

    __tablename__ = "monitoring_locks"

    name = db.Column(db.String(50), primary_key=True)
    locked_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    locked_by = db.Column(db.String(100), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(
        self,
        name: str,
        locked_by: str,
        expires_at: datetime,
        locked_at: datetime | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.name = name
        self.locked_by = locked_by
        self.expires_at = expires_at
        self.locked_at = locked_at or datetime.now(timezone.utc)

    def to_dict(self) -> dict[str, Any]:
        """Safe dictionary representation of MonitoringLock."""
        return {
            "name": self.name,
            "locked_by": self.locked_by,
            "locked_at": self.locked_at.isoformat() if self.locked_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

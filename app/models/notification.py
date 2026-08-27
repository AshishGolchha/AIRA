from datetime import datetime, timezone
from typing import Any
from app.extensions import db
from app.models.base import TimestampMixin


class NotificationDelivery(TimestampMixin, db.Model):
    """Tracks notification delivery attempts for generated alerts with channel-level idempotency and retry state."""

    __tablename__ = "notification_deliveries"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(
        db.Integer,
        db.ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel = db.Column(db.String(50), nullable=False, default="in_app")
    status = db.Column(db.String(50), nullable=False, default="delivered")  # "delivered", "failed", "pending", "skipped"
    attempt_count = db.Column(db.Integer, nullable=False, default=1)
    is_retryable = db.Column(db.Boolean, nullable=False, default=False)
    next_retry_at = db.Column(db.DateTime, nullable=True)
    attempted_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    delivered_at = db.Column(db.DateTime, nullable=True)
    failure_reason = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("alert_id", "channel", name="uq_notification_alert_channel"),
    )

    def __init__(
        self,
        alert_id: int,
        user_id: int,
        channel: str = "in_app",
        status: str = "delivered",
        failure_reason: str | None = None,
        attempt_count: int = 1,
        is_retryable: bool = False,
        next_retry_at: datetime | None = None,
        attempted_at: datetime | None = None,
        delivered_at: datetime | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.alert_id = alert_id
        self.user_id = user_id
        self.channel = channel.strip().lower() if channel else "in_app"
        self.status = status.strip().lower() if status else "delivered"
        self.failure_reason = failure_reason
        self.attempt_count = attempt_count
        self.is_retryable = is_retryable
        self.next_retry_at = next_retry_at
        self.attempted_at = attempted_at or datetime.now(timezone.utc)
        self.delivered_at = delivered_at or (datetime.now(timezone.utc) if status == "delivered" else None)

    def to_dict(self) -> dict[str, Any]:
        """Safe dictionary representation of NotificationDelivery."""
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "user_id": self.user_id,
            "channel": self.channel,
            "status": self.status,
            "attempt_count": self.attempt_count,
            "is_retryable": self.is_retryable,
            "next_retry_at": self.next_retry_at.isoformat() if self.next_retry_at else None,
            "failure_reason": self.failure_reason,
            "attempted_at": self.attempted_at.isoformat() if self.attempted_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

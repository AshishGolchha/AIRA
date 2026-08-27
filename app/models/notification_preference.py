from typing import Any
from app.extensions import db
from app.models.base import TimestampMixin


class NotificationPreference(TimestampMixin, db.Model):
    """User-scoped notification preferences controlling channels, minimum severity, and alert types."""

    __tablename__ = "notification_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    in_app_enabled = db.Column(db.Boolean, nullable=False, default=True)
    email_enabled = db.Column(db.Boolean, nullable=False, default=True)
    webhook_enabled = db.Column(db.Boolean, nullable=False, default=False)
    minimum_severity = db.Column(db.String(20), nullable=False, default="info")
    alert_types = db.Column(db.JSON, nullable=True)  # List of enabled types or None for all

    # Relationship to User
    user = db.relationship("User", back_populates="notification_preference")

    def __init__(
        self,
        user_id: int,
        in_app_enabled: bool = True,
        email_enabled: bool = True,
        webhook_enabled: bool = False,
        minimum_severity: str = "info",
        alert_types: list[str] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.in_app_enabled = in_app_enabled
        self.email_enabled = email_enabled
        self.webhook_enabled = webhook_enabled
        self.minimum_severity = minimum_severity.strip().lower() if minimum_severity else "info"
        self.alert_types = alert_types

    def to_dict(self) -> dict[str, Any]:
        """Safe dictionary representation of NotificationPreference."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "in_app_enabled": self.in_app_enabled,
            "email_enabled": self.email_enabled,
            "webhook_enabled": self.webhook_enabled,
            "minimum_severity": self.minimum_severity,
            "alert_types": self.alert_types,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

from typing import Any
from app.extensions import db
from app.models.base import TimestampMixin


class NotificationEndpoint(TimestampMixin, db.Model):
    """User-scoped notification endpoint for external delivery (e.g. webhooks)."""

    __tablename__ = "notification_endpoints"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    channel = db.Column(db.String(50), nullable=False, default="webhook")
    endpoint_url = db.Column(db.String(500), nullable=False)
    secret_key = db.Column(db.String(255), nullable=True)  # HMAC signing key (never returned in API responses)
    is_enabled = db.Column(db.Boolean, nullable=False, default=True)

    # Relationship to User
    user = db.relationship("User", back_populates="notification_endpoints")

    def __init__(
        self,
        user_id: int,
        endpoint_url: str,
        channel: str = "webhook",
        secret_key: str | None = None,
        is_enabled: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.endpoint_url = endpoint_url.strip() if endpoint_url else ""
        self.channel = channel.strip().lower() if channel else "webhook"
        self.secret_key = secret_key.strip() if secret_key else None
        self.is_enabled = is_enabled

    def to_dict(self) -> dict[str, Any]:
        """Safe dictionary representation omitting secret_key."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "channel": self.channel,
            "endpoint_url": self.endpoint_url,
            "is_enabled": self.is_enabled,
            "has_secret": bool(self.secret_key),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

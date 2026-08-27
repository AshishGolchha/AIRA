from typing import Any
from app.extensions import db
from app.models.base import TimestampMixin


class Alert(TimestampMixin, db.Model):
    """Represents a deterministic investment alert for a user's portfolio holding or watchlist security."""

    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symbol = db.Column(db.String(20), nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=True)
    alert_type = db.Column(db.String(50), nullable=False, index=True)
    severity = db.Column(db.String(20), nullable=False, default="info")
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    facts = db.Column(db.JSON, nullable=True)
    sources = db.Column(db.JSON, nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    is_dismissed = db.Column(db.Boolean, nullable=False, default=False, index=True)

    # Relationship to User
    user = db.relationship("User", back_populates="alerts")

    def __init__(
        self,
        user_id: int,
        symbol: str,
        alert_type: str,
        title: str,
        message: str,
        severity: str = "info",
        company_name: str | None = None,
        facts: dict[str, Any] | None = None,
        sources: list[dict[str, Any]] | None = None,
        is_read: bool = False,
        is_dismissed: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.symbol = symbol.strip().upper() if symbol else ""
        self.alert_type = alert_type.strip().lower() if alert_type else "info"
        self.severity = severity.strip().lower() if severity else "info"
        self.title = title
        self.message = message
        self.company_name = company_name
        self.facts = facts or {}
        self.sources = sources or []
        self.is_read = is_read
        self.is_dismissed = is_dismissed

    def to_dict(self) -> dict[str, Any]:
        """Safe dictionary representation of Alert."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "company_name": self.company_name,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "facts": self.facts or {},
            "sources": self.sources or [],
            "is_read": self.is_read,
            "is_dismissed": self.is_dismissed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

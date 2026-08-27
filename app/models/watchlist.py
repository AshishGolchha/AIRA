from app.extensions import db
from app.models.base import TimestampMixin


class WatchlistItem(TimestampMixin, db.Model):
    """Represents a financial security on a user's personal investment watchlist."""

    __tablename__ = "watchlist_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symbol = db.Column(db.String(20), nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default="normal")

    __table_args__ = (
        db.UniqueConstraint("user_id", "symbol", name="uq_watchlist_user_symbol"),
    )

    # Relationship to User
    user = db.relationship("User", back_populates="watchlist_items")

    def __init__(
        self,
        user_id: int,
        symbol: str,
        company_name: str | None = None,
        notes: str | None = None,
        priority: str = "normal",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.symbol = symbol.strip().upper() if symbol else ""
        self.company_name = company_name
        self.notes = notes
        self.priority = priority.strip().lower() if priority else "normal"

    def to_dict(self) -> dict:
        """Safe dictionary representation of watchlist item."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "company_name": self.company_name,
            "notes": self.notes,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

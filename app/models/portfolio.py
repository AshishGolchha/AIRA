from decimal import Decimal
from app.extensions import db
from app.models.base import TimestampMixin


class PortfolioHolding(TimestampMixin, db.Model):
    """Represents a financial security position owned in a user's investment portfolio."""

    __tablename__ = "portfolio_holdings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symbol = db.Column(db.String(20), nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Numeric(18, 6), nullable=False)
    average_cost = db.Column(db.Numeric(18, 4), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "symbol", name="uq_portfolio_user_symbol"),
    )

    # Relationship to User
    user = db.relationship("User", back_populates="portfolio_holdings")

    def __init__(
        self,
        user_id: int,
        symbol: str,
        quantity: Decimal | float | str,
        average_cost: Decimal | float | str,
        company_name: str | None = None,
        notes: str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.symbol = symbol.strip().upper() if symbol else ""
        self.quantity = Decimal(str(quantity)) if quantity is not None else Decimal("0")
        self.average_cost = Decimal(str(average_cost)) if average_cost is not None else Decimal("0")
        self.company_name = company_name
        self.notes = notes

    def to_dict(self) -> dict:
        """Safe dictionary representation of portfolio holding."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "company_name": self.company_name,
            "quantity": float(self.quantity) if self.quantity is not None else 0.0,
            "average_cost": float(self.average_cost) if self.average_cost is not None else 0.0,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

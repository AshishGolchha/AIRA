from app.extensions import db
from app.models.base import TimestampMixin


class ResearchRecord(TimestampMixin, db.Model):
    """Persistent record of an evidence-grounded AI investment research analysis."""

    __tablename__ = "research_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    research_query = db.Column("query", db.Text, nullable=False)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    company = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    facts = db.Column(db.JSON, nullable=False)
    fundamentals = db.Column(db.Text, nullable=True)
    valuation = db.Column(db.Text, nullable=True)
    market_context = db.Column(db.Text, nullable=True)
    risks = db.Column(db.JSON, nullable=True)
    opportunities = db.Column(db.JSON, nullable=True)
    user_context = db.Column(db.Text, nullable=True)
    sources = db.Column(db.JSON, nullable=False)

    # Relationship to User
    user = db.relationship("User", back_populates="research_records")

    def __init__(self, query: str | None = None, **kwargs):
        if query is not None:
            kwargs["research_query"] = query
        super().__init__(**kwargs)

    def to_dict(self) -> dict:
        """Full dictionary representation of the research record."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "query": self.research_query,
            "symbol": self.symbol,
            "company": self.company,
            "summary": self.summary,
            "facts": self.facts,
            "fundamentals": self.fundamentals,
            "valuation": self.valuation,
            "market_context": self.market_context,
            "risks": self.risks or [],
            "opportunities": self.opportunities or [],
            "user_context": self.user_context,
            "sources": self.sources or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_summary_dict(self) -> dict:
        """Lightweight summary representation for history listing."""
        return {
            "id": self.id,
            "company": self.company,
            "symbol": self.symbol,
            "query": self.research_query,
            "summary": self.summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

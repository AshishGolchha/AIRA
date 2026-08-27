from typing import Any
from app.extensions import db
from app.models.base import TimestampMixin


class PortfolioIntelligenceRecord(TimestampMixin, db.Model):
    """Persistent record of an evidence-grounded AI portfolio & watchlist intelligence report."""

    __tablename__ = "portfolio_intelligence_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    intelligence_query = db.Column("query", db.Text, nullable=True)
    summary = db.Column(db.Text, nullable=False)
    portfolio_overview = db.Column(db.Text, nullable=False)
    portfolio_risks = db.Column(db.JSON, nullable=True)
    portfolio_opportunities = db.Column(db.JSON, nullable=True)
    watchlist_priorities = db.Column(db.JSON, nullable=True)
    recommended_research = db.Column(db.JSON, nullable=True)
    portfolio_summary = db.Column(db.JSON, nullable=False)
    user_context = db.Column(db.Text, nullable=True)
    facts = db.Column(db.JSON, nullable=False)
    sources = db.Column(db.JSON, nullable=False)

    # Relationship to User
    user = db.relationship("User", back_populates="portfolio_intelligence_records")

    def __init__(self, query: str | None = None, **kwargs):
        if query is not None:
            kwargs["intelligence_query"] = query
        super().__init__(**kwargs)

    def _extract_symbols(self) -> list[str]:
        """Extracts unique security symbols analyzed in this intelligence report."""
        symbols = set()
        if isinstance(self.facts, dict):
            if isinstance(self.facts.get("holdings"), dict):
                symbols.update(self.facts["holdings"].keys())
            if isinstance(self.facts.get("watchlist"), dict):
                symbols.update(self.facts["watchlist"].keys())
        return sorted(list(symbols))

    def to_dict(self) -> dict[str, Any]:
        """Full dictionary representation of the portfolio intelligence report."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "query": self.intelligence_query,
            "summary": self.summary,
            "portfolio_overview": self.portfolio_overview,
            "portfolio_risks": self.portfolio_risks or [],
            "portfolio_opportunities": self.portfolio_opportunities or [],
            "watchlist_priorities": self.watchlist_priorities or [],
            "recommended_research": self.recommended_research or [],
            "portfolio_summary": self.portfolio_summary or {},
            "user_context": self.user_context,
            "facts": self.facts or {},
            "sources": self.sources or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_summary_dict(self) -> dict[str, Any]:
        """Lightweight summary representation for history listing."""
        return {
            "id": self.id,
            "query": self.intelligence_query,
            "summary": self.summary,
            "symbols_analyzed": self._extract_symbols(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_dashboard_dict(self) -> dict[str, Any]:
        """Concise summary representation for dashboard integration."""
        return {
            "id": self.id,
            "summary": self.summary,
            "symbols_analyzed": self._extract_symbols(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

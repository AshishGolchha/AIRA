from app.extensions import db
from app.models.portfolio_intelligence import PortfolioIntelligenceRecord
from app.models.user import User


def test_portfolio_intelligence_record_instantiation_and_serialization(app):
    """Verify PortfolioIntelligenceRecord model fields, serialization, and dictionary helpers."""
    user = User(email="intel_model_test@example.com")
    user.set_password("Password123!")
    db.session.add(user)
    db.session.commit()

    record = PortfolioIntelligenceRecord(
        user_id=user.id,
        query="Analyze asset allocation",
        summary="Diversified portfolio with high semiconductor exposure.",
        portfolio_overview="2 holdings across Tech sector.",
        portfolio_risks=["High valuation multiples", "Sector concentration"],
        portfolio_opportunities=["AI demand tailwinds"],
        watchlist_priorities=["Monitor AAPL support level"],
        recommended_research=["Conduct deep dive into NVDA margins"],
        portfolio_summary={"total_market_value": 5000.0, "holdings_count": 2},
        user_context="[investor] Jane | [focus] Growth",
        facts={
            "holdings": {"NVDA": {"market_value": 3000.0}, "MSFT": {"market_value": 2000.0}},
            "watchlist": {"AAPL": {"current_price": 200.0}},
        },
        sources=[{"provider": "mock", "symbol": "NVDA"}],
    )
    db.session.add(record)
    db.session.commit()

    assert record.id is not None
    assert record.created_at is not None
    assert record.user_id == user.id

    # Test full to_dict()
    d = record.to_dict()
    assert d["id"] == record.id
    assert d["user_id"] == user.id
    assert d["summary"] == "Diversified portfolio with high semiconductor exposure."
    assert d["portfolio_risks"] == ["High valuation multiples", "Sector concentration"]
    assert d["facts"]["holdings"]["NVDA"]["market_value"] == 3000.0
    assert len(d["sources"]) == 1

    # Test to_summary_dict()
    s = record.to_summary_dict()
    assert s["id"] == record.id
    assert s["query"] == "Analyze asset allocation"
    assert s["summary"] == "Diversified portfolio with high semiconductor exposure."
    assert "NVDA" in s["symbols_analyzed"]
    assert "MSFT" in s["symbols_analyzed"]
    assert "AAPL" in s["symbols_analyzed"]
    assert "facts" not in s

    # Test to_dashboard_dict()
    dash = record.to_dashboard_dict()
    assert dash["id"] == record.id
    assert dash["summary"] == "Diversified portfolio with high semiconductor exposure."
    assert "NVDA" in dash["symbols_analyzed"]
    assert dash["created_at"] is not None


def test_portfolio_intelligence_user_cascade_delete(app):
    """Verify deleting a User deletes all associated PortfolioIntelligenceRecord rows."""
    user = User(email="cascade_intel_test@example.com")
    user.set_password("Password123!")
    db.session.add(user)
    db.session.commit()

    record = PortfolioIntelligenceRecord(
        user_id=user.id,
        summary="Test summary",
        portfolio_overview="Overview",
        portfolio_summary={},
        facts={},
        sources=[],
    )
    db.session.add(record)
    db.session.commit()

    rec_id = record.id
    assert db.session.get(PortfolioIntelligenceRecord, rec_id) is not None

    db.session.delete(user)
    db.session.commit()

    assert db.session.get(PortfolioIntelligenceRecord, rec_id) is None

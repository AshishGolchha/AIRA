import pytest
from app.extensions import db
from app.models.alert import Alert
from app.models.research import ResearchRecord
from app.models.user import User, UserProfile
from app.services.dashboard_service import DashboardService
from app.services.financial.service import FinancialDataService
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider


def test_dashboard_service_empty_user(app):
    """Verify DashboardService handles empty user account gracefully."""
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    dashboard_service = DashboardService(
        portfolio_service=PortfolioService(financial_service=fin_service),
        watchlist_service=WatchlistService(financial_service=fin_service),
    )

    user = User(email="empty_dash@example.com")
    user.set_password("Password123!")
    db.session.add(user)
    db.session.commit()

    res = dashboard_service.get_dashboard(user_id=user.id)
    assert res["user"]["email"] == "empty_dash@example.com"
    assert res["portfolio"]["holdings_count"] == 0
    assert res["portfolio"]["total_market_value"] == 0.0
    assert res["watchlist"]["total_count"] == 0
    assert res["alerts"]["unread_count"] == 0
    assert res["research"]["total_reports"] == 0
    assert res["portfolio_intelligence"]["available"] is False


def test_dashboard_service_populated_user_and_bounded_limits(app):
    """Verify DashboardService aggregates populated data and bounds collection sizes."""
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    wl_service = WatchlistService(financial_service=fin_service)
    dashboard_service = DashboardService(
        portfolio_service=pf_service,
        watchlist_service=wl_service,
    )

    user = User(email="populated_dash@example.com")
    user.set_password("Password123!")
    profile = UserProfile(user=user, display_name="Jane Investor")
    profile.risk_preference = "aggressive"
    db.session.add_all([user, profile])
    db.session.commit()

    # 1. Add 6 portfolio holdings (should be bounded to top 5)
    for sym in ["NVDA", "AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]:
        pf_service.create_holding(user_id=user.id, symbol=sym, quantity=10, average_cost=50)

    # 2. Add 6 watchlist items (should be bounded to 5)
    for sym in ["META", "NFLX", "AMD", "INTC", "CRM", "ORCL"]:
        wl_service.add_item(user_id=user.id, symbol=sym, priority="high" if sym in ("META", "NFLX") else "normal")

    # 3. Add 6 alerts (should be bounded to 5)
    for i in range(6):
        a = Alert(
            user_id=user.id,
            symbol=f"SYM{i}",
            alert_type="price_move",
            severity="critical" if i == 0 else "info",
            title=f"Alert {i}",
            message=f"Message {i}",
        )
        db.session.add(a)

    # 4. Add 6 research records (should be bounded to 5)
    for i in range(6):
        r = ResearchRecord(
            user_id=user.id,
            query=f"Query {i}",
            symbol=f"R_SYM{i}",
            company=f"Company {i}",
            summary=f"Summary {i}",
            facts={"pe_ratio": 25.0},
            sources=[{"provider": "mock"}],
        )
        db.session.add(r)
    db.session.commit()

    # Run dashboard
    res = dashboard_service.get_dashboard(user_id=user.id)

    assert res["user"]["name"] == "Jane Investor"
    assert res["user"]["risk_tolerance"] == "aggressive"

    # Portfolio checks
    assert res["portfolio"]["holdings_count"] == 6
    assert len(res["portfolio"]["top_holdings"]) == 5
    assert res["portfolio"]["total_market_value"] > 0

    # Watchlist checks
    assert res["watchlist"]["total_count"] == 6
    assert res["watchlist"]["high_priority_count"] == 2
    assert len(res["watchlist"]["items"]) == 5

    # Alert checks
    assert res["alerts"]["unread_count"] == 6
    assert res["alerts"]["critical_count"] == 1
    assert len(res["alerts"]["recent"]) == 5

    # Research checks
    assert res["research"]["total_reports"] == 6
    assert len(res["research"]["recent"]) == 5

    # Notifications checks
    assert "preferences" in res["notifications"]
    assert "in_app" in res["notifications"]["enabled_channels"]

    # Summary checks
    summary = dashboard_service.get_summary(user_id=user.id)
    assert summary["holdings_count"] == 6
    assert summary["watchlist_count"] == 6
    assert summary["unread_alerts_count"] == 6
    assert summary["critical_alerts_count"] == 1
    assert summary["research_reports_count"] == 6


def test_dashboard_service_invalid_user_id(app):
    """Verify DashboardService rejects invalid or non-existent user IDs."""
    dashboard_service = DashboardService()
    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        dashboard_service.get_dashboard(user_id=-1)

    with pytest.raises(ValueError, match="not found"):
        dashboard_service.get_dashboard(user_id=99999)

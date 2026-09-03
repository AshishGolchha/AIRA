from app.extensions import db
from app.models.alert import Alert
from app.models.notification import NotificationDelivery
from app.models.portfolio_intelligence import PortfolioIntelligenceRecord
from app.models.research import ResearchRecord
from app.services.financial.service import FinancialDataService
from app.services.portfolio_intelligence_service import PortfolioIntelligenceService
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider


def _register_user(client, email: str = "dash_user@example.com", password: str = "Password123!"):
    res = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    return res.get_json()["data"]["access_token"]


def test_dashboard_endpoint_authenticated_success(app, client):
    """Verify GET /api/v1/dashboard returns 200 and all structured domains."""
    token = _register_user(client, "dash_main@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Add a holding
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers=headers,
    )

    # Add a watchlist item
    client.post(
        "/api/v1/watchlist",
        json={"symbol": "TSLA", "priority": "high"},
        headers=headers,
    )

    # Trigger alerts check to create an alert
    client.post(
        "/api/v1/alerts/check",
        headers=headers,
    )

    # Call Dashboard Endpoint (No intelligence generated yet)
    resp = client.get("/api/v1/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]

    # Verify all 8 core domains are present
    assert "user" in data
    assert "portfolio" in data
    assert "watchlist" in data
    assert "alerts" in data
    assert "research" in data
    assert "notifications" in data
    assert "monitoring" in data
    assert "portfolio_intelligence" in data

    # Verify field structures
    assert data["user"]["email"] == "dash_main@example.com"
    assert data["portfolio"]["holdings_count"] == 1
    assert data["watchlist"]["total_count"] == 1
    assert data["watchlist"]["high_priority_count"] == 1
    assert data["portfolio_intelligence"]["available"] is False


def test_dashboard_with_latest_portfolio_intelligence(app, client):
    """Verify GET /api/v1/dashboard displays latest intelligence when generated."""
    token = _register_user(client, "dash_intel@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Inject mock intelligence runner
    def mock_runner(**kwargs):
        return {
            "summary": "High conviction bullish tech portfolio.",
            "portfolio_overview": "Overview text.",
            "portfolio_risks": ["Concentration in NVDA"],
            "portfolio_opportunities": ["AI market scale"],
            "watchlist_priorities": ["Monitor TSLA"],
            "recommended_research": ["Deep dive on NVDA"],
        }

    fin_service = FinancialDataService(provider=MockFinancialProvider())
    port_service = PortfolioService(financial_service=fin_service)
    watch_service = WatchlistService()

    app.extensions["portfolio_intelligence_service"] = PortfolioIntelligenceService(
        portfolio_service=port_service,
        watchlist_service=watch_service,
        financial_service=fin_service,
        memory_service=app.extensions.get("memory_service"),
        crew_runner=mock_runner,
    )

    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers=headers,
    )

    # Generate intelligence
    client.post("/api/v1/portfolio/intelligence", headers=headers)

    # Call dashboard
    resp = client.get("/api/v1/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]

    assert data["portfolio_intelligence"]["available"] is True
    assert data["portfolio_intelligence"]["latest"] is not None
    assert "NVDA" in data["portfolio_intelligence"]["latest"]["symbols_analyzed"]
    assert data["portfolio_intelligence"]["latest"]["summary"] == "High conviction bullish tech portfolio."


def test_dashboard_summary_endpoint(app, client):
    """Verify GET /api/v1/dashboard/summary returns 200 with lightweight metrics."""
    token = _register_user(client, "dash_summary@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "AAPL", "quantity": 5, "average_cost": 150},
        headers=headers,
    )

    resp = client.get("/api/v1/dashboard/summary", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]

    assert "portfolio_market_value" in data
    assert "holdings_count" in data
    assert data["holdings_count"] == 1
    assert "watchlist_count" in data
    assert "unread_alerts_count" in data
    assert "monitoring_enabled" in data


def test_dashboard_unauthenticated_rejected(app, client):
    """Verify unauthenticated requests are rejected with 401."""
    resp1 = client.get("/api/v1/dashboard")
    assert resp1.status_code == 401

    resp2 = client.get("/api/v1/dashboard/summary")
    assert resp2.status_code == 401


def test_dashboard_multi_tenant_isolation(app, client):
    """Verify User A and User B cannot see each other's data in the dashboard."""
    token_a = _register_user(client, "dash_user_a@example.com")
    token_b = _register_user(client, "dash_user_b@example.com")

    # User A adds NVDA
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # User B adds TSLA
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "TSLA", "quantity": 20, "average_cost": 200},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    # Check User A dashboard
    resp_a = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token_a}"})
    data_a = resp_a.get_json()["data"]
    symbols_a = {h["symbol"] for h in data_a["portfolio"]["top_holdings"]}
    assert "NVDA" in symbols_a
    assert "TSLA" not in symbols_a

    # Check User B dashboard
    resp_b = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token_b}"})
    data_b = resp_b.get_json()["data"]
    symbols_b = {h["symbol"] for h in data_b["portfolio"]["top_holdings"]}
    assert "TSLA" in symbols_b
    assert "NVDA" not in symbols_b


def test_dashboard_is_strictly_read_only(app, client):
    """Verify calling GET /api/v1/dashboard creates 0 new database rows."""
    token = _register_user(client, "readonly_dash@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers=headers,
    )

    initial_alerts_count = Alert.query.count()
    initial_deliveries_count = NotificationDelivery.query.count()
    initial_research_count = ResearchRecord.query.count()
    initial_intel_count = PortfolioIntelligenceRecord.query.count()

    # Call dashboard 3 times
    for _ in range(3):
        resp = client.get("/api/v1/dashboard", headers=headers)
        assert resp.status_code == 200

    # Ensure 0 new records were created
    assert Alert.query.count() == initial_alerts_count
    assert NotificationDelivery.query.count() == initial_deliveries_count
    assert ResearchRecord.query.count() == initial_research_count
    assert PortfolioIntelligenceRecord.query.count() == initial_intel_count

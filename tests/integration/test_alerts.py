import pytest
from app.services.alert_service import AlertService
from app.services.financial.service import FinancialDataService
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture(autouse=True)
def setup_alerts_service(app):
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    wl_service = WatchlistService(financial_service=fin_service)
    alert_service = AlertService(
        portfolio_service=pf_service,
        watchlist_service=wl_service,
        financial_service=fin_service,
    )

    app.extensions["alert_service"] = alert_service
    app.extensions["portfolio_service"] = pf_service
    app.extensions["watchlist_service"] = wl_service
    app.extensions["financial_service"] = fin_service
    yield alert_service


def _get_auth_token(client, email: str = "alert_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_alerts_check_authenticated_success(client):
    """Verify authenticated user can run alert checks and receive created alerts."""
    token = _get_auth_token(client, "alerts_check_auth@example.com")

    # Add a portfolio holding (+50% gain in mock)
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Add a watchlist item (+3.45% price move in mock)
    client.post(
        "/api/v1/watchlist",
        json={"symbol": "AAPL", "priority": "high"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Check alerts with price_threshold=1.0, gain_loss_threshold=10.0
    res = client.post(
        "/api/v1/alerts/check",
        json={"price_threshold": 1.0, "gain_loss_threshold": 10.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["created_count"] >= 2
    symbols = {a["symbol"] for a in data["alerts"]}
    assert "NVDA" in symbols
    assert "AAPL" in symbols


def test_alerts_unauthenticated_rejected(client):
    """Verify unauthenticated requests are rejected with 401."""
    assert client.post("/api/v1/alerts/check").status_code == 401
    assert client.get("/api/v1/alerts").status_code == 401
    assert client.get("/api/v1/alerts/1").status_code == 401
    assert client.put("/api/v1/alerts/1/read").status_code == 401
    assert client.put("/api/v1/alerts/1/dismiss").status_code == 401


def test_alerts_empty_account_returns_zero(client):
    """Verify checking empty accounts returns 0 alerts safely."""
    token = _get_auth_token(client, "alerts_empty@example.com")
    res = client.post(
        "/api/v1/alerts/check",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.get_json()["data"]["created_count"] == 0
    assert res.get_json()["data"]["alerts"] == []


def test_alerts_list_get_read_dismiss(client):
    """Verify full CRUD and status update lifecycle via HTTP."""
    token = _get_auth_token(client, "alerts_crud@example.com")

    # Add holding to trigger alerts
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    )

    check_res = client.post(
        "/api/v1/alerts/check",
        json={"gain_loss_threshold": 10.0, "price_threshold": 2.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    alert_id = check_res.get_json()["data"]["alerts"][0]["id"]

    # 1. Get alert by ID
    get_res = client.get(f"/api/v1/alerts/{alert_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 200
    assert get_res.get_json()["data"]["alert"]["id"] == alert_id
    assert get_res.get_json()["data"]["alert"]["is_read"] is False

    # 2. Mark as read
    read_res = client.put(f"/api/v1/alerts/{alert_id}/read", headers={"Authorization": f"Bearer {token}"})
    assert read_res.status_code == 200
    assert read_res.get_json()["data"]["alert"]["is_read"] is True

    # 3. List alerts with unread_only=true
    unread_res = client.get("/api/v1/alerts?unread_only=true", headers={"Authorization": f"Bearer {token}"})
    assert unread_res.status_code == 200
    assert alert_id not in [a["id"] for a in unread_res.get_json()["data"]["alerts"]]

    # 4. Dismiss alert
    dismiss_res = client.put(f"/api/v1/alerts/{alert_id}/dismiss", headers={"Authorization": f"Bearer {token}"})
    assert dismiss_res.status_code == 200
    assert dismiss_res.get_json()["data"]["alert"]["is_dismissed"] is True

    # 5. List alerts with include_dismissed=false
    active_res = client.get("/api/v1/alerts?include_dismissed=false", headers={"Authorization": f"Bearer {token}"})
    assert alert_id not in [a["id"] for a in active_res.get_json()["data"]["alerts"]]


def test_alerts_multi_tenant_isolation(client):
    """
    CRITICAL MULTI-TENANT ISOLATION TEST:
    User A cannot view, retrieve, mark read, or dismiss User B's alerts.
    """
    token_a = _get_auth_token(client, "user_a_alerts@example.com")
    token_b = _get_auth_token(client, "user_b_alerts@example.com")

    # Create holding and alert for User A
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    check_a = client.post(
        "/api/v1/alerts/check",
        json={"gain_loss_threshold": 10.0},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    alert_a_id = check_a.get_json()["data"]["alerts"][0]["id"]

    # User B tries to view User A's alert by ID -> 404
    get_b = client.get(f"/api/v1/alerts/{alert_a_id}", headers={"Authorization": f"Bearer {token_b}"})
    assert get_b.status_code == 404

    # User B tries to mark User A's alert as read -> 404
    read_b = client.put(f"/api/v1/alerts/{alert_a_id}/read", headers={"Authorization": f"Bearer {token_b}"})
    assert read_b.status_code == 404

    # User B tries to dismiss User A's alert -> 404
    dismiss_b = client.put(f"/api/v1/alerts/{alert_a_id}/dismiss", headers={"Authorization": f"Bearer {token_b}"})
    assert dismiss_b.status_code == 404

    # User B's alert list must be completely empty
    list_b = client.get("/api/v1/alerts", headers={"Authorization": f"Bearer {token_b}"})
    assert list_b.status_code == 200
    assert list_b.get_json()["data"]["total_count"] == 0


def test_alerts_client_supplied_user_id_ignored(client):
    """Verify that client-supplied user_id in payload has zero effect on alert ownership."""
    token = _get_auth_token(client, "client_user_id_test@example.com")

    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Attempt to inject user_id: 999
    res = client.post(
        "/api/v1/alerts/check",
        json={"user_id": 999, "gain_loss_threshold": 10.0},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    alerts = res.get_json()["data"]["alerts"]
    assert len(alerts) >= 1
    # Alert is owned by authenticated user, not 999
    for a in alerts:
        get_res = client.get(f"/api/v1/alerts/{a['id']}", headers={"Authorization": f"Bearer {token}"})
        assert get_res.status_code == 200

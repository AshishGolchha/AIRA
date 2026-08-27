import pytest
from app.extensions import db
from app.models.notification import NotificationDelivery
from app.models.user import User
from app.services.alert_service import AlertService
from app.services.financial.service import FinancialDataService
from app.services.monitoring_service import MonitoringService
from app.services.notifications import NotificationService
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture(autouse=True)
def setup_monitoring_infrastructure(app):
    fin_service = FinancialDataService(provider=MockFinancialProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    wl_service = WatchlistService(financial_service=fin_service)
    alert_service = AlertService(
        portfolio_service=pf_service,
        watchlist_service=wl_service,
        financial_service=fin_service,
    )
    notif_service = NotificationService()
    mon_service = MonitoringService(
        alert_service=alert_service,
        notification_service=notif_service,
    )

    app.extensions["monitoring_service"] = mon_service
    app.extensions["alert_service"] = alert_service
    app.extensions["notification_service"] = notif_service
    app.extensions["portfolio_service"] = pf_service
    app.extensions["watchlist_service"] = wl_service
    app.extensions["financial_service"] = fin_service

    yield mon_service


def _get_auth_token(client, email: str = "monitoring_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_monitoring_multi_user_batch_execution(app, client):
    """Verify batch monitoring checks multiple users and creates alerts and notifications."""
    mon_service = app.extensions["monitoring_service"]

    token_a = _get_auth_token(client, "user_a_mon@example.com")
    token_b = _get_auth_token(client, "user_b_mon@example.com")

    # User A has NVDA holding (+50% gain)
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    # User B has TSLA watchlist item (+1.01% price move)
    client.post(
        "/api/v1/watchlist",
        json={"symbol": "TSLA", "priority": "high"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    # Execute scheduled monitoring run with price_threshold=1.0, gain_loss_threshold=10.0
    run_stats = mon_service.run_alert_monitoring(price_threshold=1.0, gain_loss_threshold=10.0)
    assert run_stats["status"] == "completed"
    assert run_stats["users_checked"] >= 2
    assert run_stats["users_succeeded"] >= 2
    assert run_stats["users_failed"] == 0
    assert run_stats["alerts_generated"] >= 2

    # Verify User A received NVDA alerts and notifications
    alerts_a = client.get("/api/v1/alerts", headers={"Authorization": f"Bearer {token_a}"}).get_json()["data"]["alerts"]
    assert len(alerts_a) >= 1
    assert "NVDA" in {a["symbol"] for a in alerts_a}

    # Verify User B received TSLA alerts and notifications
    alerts_b = client.get("/api/v1/alerts", headers={"Authorization": f"Bearer {token_b}"}).get_json()["data"]["alerts"]
    assert len(alerts_b) >= 1
    assert "TSLA" in {a["symbol"] for a in alerts_b}

    # Multi-tenant check: User A never sees TSLA, User B never sees NVDA
    assert "TSLA" not in {a["symbol"] for a in alerts_a}
    assert "NVDA" not in {a["symbol"] for a in alerts_b}


def test_monitoring_repeated_runs_are_idempotent(app, client):
    """Verify repeated monitoring runs create 0 duplicate alerts and 0 duplicate notifications."""
    mon_service = app.extensions["monitoring_service"]
    token = _get_auth_token(client, "idempotent_mon@example.com")

    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Run 1: creates alerts and notification deliveries
    run1 = mon_service.run_alert_monitoring(price_threshold=1.0, gain_loss_threshold=10.0)
    initial_alerts = run1["alerts_generated"]
    assert initial_alerts >= 1

    deliv_count_1 = NotificationDelivery.query.count()
    assert deliv_count_1 >= 1

    # Run 2: immediately repeated run on unchanged data must create 0 new alerts & 0 new deliveries
    run2 = mon_service.run_alert_monitoring(price_threshold=1.0, gain_loss_threshold=10.0)
    assert run2["alerts_generated"] == 0

    deliv_count_2 = NotificationDelivery.query.count()
    assert deliv_count_2 == deliv_count_1


def test_monitoring_disabled_user_is_skipped(app, client):
    """Verify user with alerts_enabled=False is skipped by batch monitoring."""
    mon_service = app.extensions["monitoring_service"]
    token = _get_auth_token(client, "disabled_alerts_user@example.com")

    # Disable alerts for this user directly in db
    user = User.query.filter_by(email="disabled_alerts_user@example.com").first()
    user.alerts_enabled = False
    db.session.commit()

    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Run monitoring
    mon_service.run_alert_monitoring(price_threshold=1.0, gain_loss_threshold=10.0)

    # User alerts list should remain empty
    alerts = client.get("/api/v1/alerts", headers={"Authorization": f"Bearer {token}"}).get_json()["data"]["alerts"]
    assert len(alerts) == 0

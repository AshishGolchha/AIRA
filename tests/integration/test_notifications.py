import pytest
from app.services.alert_service import AlertService
from app.services.financial.service import FinancialDataService
from app.services.monitoring_service import MonitoringService
from app.services.notifications import (
    EmailNotificationProvider,
    InAppNotificationProvider,
    NotificationService,
    WebhookNotificationProvider,
)
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService
from tests.unit.test_financial_service import MockFinancialProvider


@pytest.fixture(autouse=True)
def setup_multi_channel_notifications(app):
    email_dispatched = []
    webhook_dispatched = []

    email_prov = EmailNotificationProvider(
        enabled=True,
        send_fn=lambda p: email_dispatched.append(p) or True,
    )
    webhook_prov = WebhookNotificationProvider(
        dispatch_fn=lambda p: webhook_dispatched.append(p) or True,
        allow_http_in_tests=True,
    )
    in_app_prov = InAppNotificationProvider()

    fin_service = FinancialDataService(provider=MockFinancialProvider())
    pf_service = PortfolioService(financial_service=fin_service)
    wl_service = WatchlistService(financial_service=fin_service)
    alert_service = AlertService(
        portfolio_service=pf_service,
        watchlist_service=wl_service,
        financial_service=fin_service,
    )
    notif_service = NotificationService(
        providers={
            "in_app": in_app_prov,
            "email": email_prov,
            "webhook": webhook_prov,
        }
    )
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
    app.extensions["email_dispatched"] = email_dispatched
    app.extensions["webhook_dispatched"] = webhook_dispatched

    yield {
        "monitoring_service": mon_service,
        "notification_service": notif_service,
        "email_dispatched": email_dispatched,
        "webhook_dispatched": webhook_dispatched,
    }


def _get_auth_token(client, email: str = "delivery_user@example.com"):
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Password123!"},
    )
    return reg.get_json()["data"]["access_token"]


def test_full_multi_channel_alert_and_delivery_history(app, client):
    """Verify end-to-end alert trigger delivers to enabled channels and appears in delivery history."""
    token = _get_auth_token(client, "multi_delivery_user@example.com")
    mon_service = app.extensions["monitoring_service"]

    # 1. Enable webhook channel and configure an endpoint
    client.put(
        "/api/v1/notifications/preferences",
        json={
            "in_app_enabled": True,
            "email_enabled": True,
            "webhook_enabled": True,
            "minimum_severity": "info",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/api/v1/notifications/endpoints",
        json={"endpoint_url": "https://api.example.com/webhooks/alerts"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 2. Add holding triggering gain alert (+50%)
    client.post(
        "/api/v1/portfolio/holdings",
        json={"symbol": "NVDA", "quantity": 10, "average_cost": 100},
        headers={"Authorization": f"Bearer {token}"},
    )

    # 3. Run automated monitoring
    run_stats = mon_service.run_alert_monitoring(price_threshold=1.0, gain_loss_threshold=10.0)
    assert run_stats["status"] == "completed"
    assert run_stats["alerts_generated"] >= 1

    # 4. Verify external providers were called
    assert len(app.extensions["email_dispatched"]) >= 1
    assert len(app.extensions["webhook_dispatched"]) >= 1

    # 5. Check GET /api/v1/notifications/deliveries
    deliv_resp = client.get(
        "/api/v1/notifications/deliveries",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deliv_resp.status_code == 200
    deliveries = deliv_resp.get_json()["data"]["deliveries"]
    assert len(deliveries) >= 3

    channels_recorded = {d["channel"] for d in deliveries}
    assert "in_app" in channels_recorded
    assert "email" in channels_recorded
    assert "webhook" in channels_recorded

import pytest
from app.extensions import db
from app.models.alert import Alert
from app.models.notification import NotificationDelivery
from app.models.notification_endpoint import NotificationEndpoint
from app.models.user import User
from app.services.notifications.base import BaseNotificationProvider
from app.services.notifications.email import EmailNotificationProvider
from app.services.notifications.service import NotificationService
from app.services.notifications.webhook import WebhookNotificationProvider


class MockFailingNotificationProvider(BaseNotificationProvider):
    def send_alert_notification(self, user_id: int, alert: dict, **kwargs) -> bool:
        raise ConnectionError("SMTP gateway unreachable")


def test_notification_service_validation(app):
    """Verify input validation on process_alert."""
    service = NotificationService()
    with pytest.raises(ValueError, match="Valid authenticated user ID is required"):
        service.process_alert(user_id=0, alert={"id": 1})

    with pytest.raises(ValueError, match="Valid alert data with ID is required"):
        service.process_alert(user_id=1, alert={})


def test_notification_service_successful_delivery_and_idempotency(app):
    """Verify delivery creation and duplicate prevention."""
    service = NotificationService()

    alert = Alert(
        user_id=1,
        symbol="NVDA",
        alert_type="price_move",
        title="Price Move",
        message="NVDA moved 5%",
    )
    db.session.add(alert)
    db.session.commit()
    alert_dict = alert.to_dict()

    # 1. First delivery attempt -> delivered
    res1 = service.process_alert(user_id=1, alert=alert_dict, channel="in_app")
    assert res1["status"] == "delivered"
    assert res1["channel"] == "in_app"
    assert res1["delivered_at"] is not None

    # Verify persisted in database
    delivery = NotificationDelivery.query.filter_by(alert_id=alert.id, channel="in_app").first()
    assert delivery is not None
    assert delivery.status == "delivered"

    # 2. Repeated delivery attempt -> skipped due to idempotency
    res2 = service.process_alert(user_id=1, alert=alert_dict, channel="in_app")
    assert res2["status"] == "skipped"
    assert res2["reason"] == "already_delivered"


def test_notification_service_skips_dismissed_alert(app):
    """Verify dismissed alert is not delivered."""
    service = NotificationService()
    alert = Alert(
        user_id=1,
        symbol="AAPL",
        alert_type="watchlist_move",
        title="Watchlist Move",
        message="AAPL moved",
        is_dismissed=True,
    )
    db.session.add(alert)
    db.session.commit()

    res = service.process_alert(user_id=1, alert=alert.to_dict(), channel="in_app")
    assert res["status"] == "skipped"
    assert res["reason"] == "alert_dismissed"


def test_notification_service_provider_failure_does_not_corrupt_alert(app):
    """Verify provider failure records status=failed without corrupting Alert."""
    service = NotificationService(provider=MockFailingNotificationProvider())
    alert = Alert(
        user_id=1,
        symbol="MSFT",
        alert_type="portfolio_loss",
        title="Loss Alert",
        message="MSFT loss",
    )
    db.session.add(alert)
    db.session.commit()

    res = service.process_alert(user_id=1, alert=alert.to_dict(), channel="in_app")
    assert res["status"] == "failed"
    assert "Provider exception" in res["failure_reason"]

    # Verify Alert is completely intact
    persisted_alert = db.session.get(Alert, alert.id)
    assert persisted_alert is not None
    assert persisted_alert.symbol == "MSFT"


def test_notification_service_severity_filtering(app):
    """Verify alert below user's minimum severity is skipped."""
    service = NotificationService()

    u = User(email="severity_user@example.com")
    u.set_password("Password123!")
    db.session.add(u)
    db.session.commit()

    # User requires minimum 'warning' severity
    service.update_preferences(user_id=u.id, minimum_severity="warning")

    # Alert with 'info' severity
    info_alert = Alert(
        user_id=u.id,
        symbol="GOOGL",
        alert_type="price_move",
        severity="info",
        title="Google Info",
        message="Info move",
    )
    db.session.add(info_alert)
    db.session.commit()

    res = service.process_alert(user_id=u.id, alert=info_alert.to_dict(), channel="in_app")
    assert res["status"] == "skipped"
    assert res["reason"] == "below_minimum_severity"


def test_notification_service_alert_type_filtering(app):
    """Verify alert not in user's enabled alert types is skipped."""
    service = NotificationService()

    u = User(email="type_filter_user@example.com")
    u.set_password("Password123!")
    db.session.add(u)
    db.session.commit()

    # User only wants 'portfolio_loss'
    service.update_preferences(user_id=u.id, alert_types=["portfolio_loss"])

    gain_alert = Alert(
        user_id=u.id,
        symbol="NVDA",
        alert_type="portfolio_gain",
        severity="info",
        title="Gain Alert",
        message="Gain move",
    )
    db.session.add(gain_alert)
    db.session.commit()

    res = service.process_alert(user_id=u.id, alert=gain_alert.to_dict(), channel="in_app")
    assert res["status"] == "skipped"
    assert res["reason"] == "alert_type_not_enabled"


def test_notification_service_multi_channel_dispatch(app):
    """Verify multi-channel dispatch across in_app, email, and webhook."""
    email_sent = []
    webhook_sent = []

    email_prov = EmailNotificationProvider(enabled=True, send_fn=lambda p: email_sent.append(p) or True)
    webhook_prov = WebhookNotificationProvider(
        dispatch_fn=lambda p: webhook_sent.append(p) or True,
        allow_http_in_tests=True,
    )

    service = NotificationService(
        providers={
            "in_app": NotificationService().providers["in_app"],
            "email": email_prov,
            "webhook": webhook_prov,
        }
    )

    u = User(email="multi_channel@example.com")
    u.set_password("Password123!")
    db.session.add(u)
    db.session.commit()

    # Configure endpoint and preferences
    ep = NotificationEndpoint(
        user_id=u.id,
        endpoint_url="https://api.example.com/webhook",
        is_enabled=True,
    )
    db.session.add(ep)
    db.session.commit()

    service.update_preferences(
        user_id=u.id,
        in_app_enabled=True,
        email_enabled=True,
        webhook_enabled=True,
    )

    alert = Alert(
        user_id=u.id,
        symbol="NVDA",
        alert_type="portfolio_gain",
        severity="warning",
        title="NVDA Gain",
        message="NVDA gained 20%",
    )
    db.session.add(alert)
    db.session.commit()

    results = service.process_alert(user_id=u.id, alert=alert.to_dict())
    assert isinstance(results, list)
    assert len(results) == 3

    channels_delivered = {r["channel"] for r in results if r["status"] == "delivered"}
    assert "in_app" in channels_delivered
    assert "email" in channels_delivered
    assert "webhook" in channels_delivered

    assert len(email_sent) == 1
    assert len(webhook_sent) == 1

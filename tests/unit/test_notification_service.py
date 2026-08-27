import pytest
from app.extensions import db
from app.models.alert import Alert
from app.models.notification import NotificationDelivery
from app.services.notifications.base import BaseNotificationProvider
from app.services.notifications.service import NotificationService


class MockFailingNotificationProvider(BaseNotificationProvider):
    def send_alert_notification(self, user_id: int, alert: dict) -> bool:
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

    res = service.process_alert(user_id=1, alert=alert.to_dict())
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

    res = service.process_alert(user_id=1, alert=alert.to_dict())
    assert res["status"] == "failed"
    assert "Provider exception" in res["failure_reason"]

    # Verify Alert is completely intact
    persisted_alert = db.session.get(Alert, alert.id)
    assert persisted_alert is not None
    assert persisted_alert.symbol == "MSFT"

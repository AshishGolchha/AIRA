from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models.alert import Alert
from app.models.notification import NotificationDelivery
from app.services.notifications.base import BaseNotificationProvider
from app.services.notifications.service import NotificationService


class FlakyNotificationProvider(BaseNotificationProvider):
    def __init__(self):
        self.should_fail = True
        self.attempts = 0

    def send_alert_notification(self, user_id: int, alert: dict, **kwargs) -> bool:
        self.attempts += 1
        if self.should_fail:
            raise ConnectionError("Temporary upstream network glitch (503 Service Unavailable)")
        return True


def test_transient_failure_and_retry_lifecycle(app):
    """Verify transient notification failure records retry metadata and updates in-place on retry."""
    flaky_prov = FlakyNotificationProvider()
    service = NotificationService(provider=flaky_prov)

    alert = Alert(
        user_id=1,
        symbol="NVDA",
        alert_type="portfolio_gain",
        severity="info",
        title="NVDA Up",
        message="NVDA gained 15%",
    )
    db.session.add(alert)
    db.session.commit()

    # 1. Initial Attempt -> fails transiently
    res1 = service.process_alert(user_id=1, alert=alert.to_dict(), channel="in_app")
    assert res1["status"] == "failed"
    assert res1["is_retryable"] is True
    assert res1["attempt_count"] == 1
    assert res1["next_retry_at"] is not None

    deliv_id = res1["id"]

    # Verify single delivery in database
    assert NotificationDelivery.query.count() == 1
    deliv = db.session.get(NotificationDelivery, deliv_id)
    assert deliv.status == "failed"
    assert deliv.attempt_count == 1

    # 2. Simulate passage of time for next_retry_at
    deliv.next_retry_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.session.commit()

    # 3. Flaky provider recovers
    flaky_prov.should_fail = False

    # 4. Execute retry
    retry_res = service.retry_failed_deliveries()
    assert retry_res["retried_count"] == 1
    assert retry_res["succeeded_count"] == 1
    assert retry_res["failed_count"] == 0

    # 5. Verify NO duplicate delivery row was created and existing row was updated
    assert NotificationDelivery.query.count() == 1
    updated_deliv = db.session.get(NotificationDelivery, deliv_id)
    assert updated_deliv.status == "delivered"
    assert updated_deliv.attempt_count == 2
    assert updated_deliv.is_retryable is False
    assert updated_deliv.next_retry_at is None
    assert updated_deliv.delivered_at is not None

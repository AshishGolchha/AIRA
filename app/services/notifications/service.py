from typing import Any
from flask import current_app, has_app_context

from app.extensions import db
from app.models.notification import NotificationDelivery
from app.services.notifications.base import BaseNotificationProvider
from app.services.notifications.in_app import InAppNotificationProvider


class NotificationService:
    """Orchestrates notification delivery attempts, status tracking, and channel-level idempotency."""

    def __init__(self, provider: BaseNotificationProvider | None = None):
        self.provider = provider or InAppNotificationProvider()

    def process_alert(
        self,
        user_id: int,
        alert: dict[str, Any],
        channel: str = "in_app",
    ) -> dict[str, Any]:
        """Processes and delivers an alert notification with idempotency and failure isolation."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")
        if not alert or not alert.get("id"):
            raise ValueError("Valid alert data with ID is required.")

        alert_id = alert["id"]
        channel = channel.strip().lower() if channel else "in_app"

        # 1. Skip dismissed alerts
        if alert.get("is_dismissed"):
            return {
                "alert_id": alert_id,
                "user_id": user_id,
                "channel": channel,
                "status": "skipped",
                "reason": "alert_dismissed",
            }

        # 2. Idempotency Check: Avoid duplicate deliveries for the same alert and channel
        existing = NotificationDelivery.query.filter_by(
            alert_id=alert_id, channel=channel
        ).first()
        if existing:
            return {
                "alert_id": alert_id,
                "user_id": user_id,
                "channel": channel,
                "status": "skipped",
                "reason": "already_delivered",
                "delivery_id": existing.id,
            }

        # 3. Attempt Delivery via Provider
        success = False
        failure_reason = None
        try:
            success = bool(self.provider.send_alert_notification(user_id=user_id, alert=alert))
            if not success:
                failure_reason = "Notification provider returned delivery failure."
        except Exception as e:
            failure_reason = f"Provider exception: {str(e)}"
            success = False
            if has_app_context():
                current_app.logger.warning(
                    f"Notification provider failed for alert {alert_id}, user {user_id}: {e}"
                )

        # 4. Record Notification Delivery Attempt
        delivery = NotificationDelivery(
            alert_id=alert_id,
            user_id=user_id,
            channel=channel,
            status="delivered" if success else "failed",
            failure_reason=failure_reason,
        )
        db.session.add(delivery)
        db.session.commit()

        return delivery.to_dict()

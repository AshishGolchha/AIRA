from typing import Any
from app.services.notifications.base import BaseNotificationProvider


class InAppNotificationProvider(BaseNotificationProvider):
    """In-app alert notification provider (delivers alerts to user's in-app inbox)."""

    def send_alert_notification(self, user_id: int, alert: dict[str, Any]) -> bool:
        """In-app notification delivery confirmation."""
        if not user_id or not alert or not alert.get("id"):
            return False
        return True

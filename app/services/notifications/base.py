from abc import ABC, abstractmethod
from typing import Any


class BaseNotificationProvider(ABC):
    """Abstract interface for external/internal notification delivery channels."""

    @abstractmethod
    def send_alert_notification(
        self,
        user_id: int,
        alert: dict[str, Any],
        **kwargs,
    ) -> bool:
        """
        Sends an alert notification to the user or destination endpoint.
        Returns True if delivery succeeded, False if delivery failed.
        """
        pass

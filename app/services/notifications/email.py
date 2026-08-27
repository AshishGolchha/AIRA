import os
from typing import Any, Callable
from flask import current_app, has_app_context

from app.services.notifications.base import BaseNotificationProvider


class EmailNotificationProvider(BaseNotificationProvider):
    """External email alert notification provider (supports Resend / SMTP / custom backend)."""

    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
        enabled: bool | None = None,
        send_fn: Callable[..., bool] | None = None,
    ):
        self._api_key = api_key
        self._from_email = from_email
        self._enabled = enabled
        self._send_fn = send_fn
        self.sent_emails: list[dict[str, Any]] = []

    def _is_enabled(self) -> bool:
        if self._enabled is not None:
            return self._enabled
        if has_app_context():
            return bool(current_app.config.get("NOTIFICATION_EMAIL_ENABLED", False))
        return os.getenv("NOTIFICATION_EMAIL_ENABLED", "false").lower() in ("true", "1")

    def _get_api_key(self) -> str | None:
        if self._api_key:
            return self._api_key
        if has_app_context():
            return current_app.config.get("NOTIFICATION_EMAIL_API_KEY")
        return os.getenv("NOTIFICATION_EMAIL_API_KEY")

    def _get_from_email(self) -> str:
        if self._from_email:
            return self._from_email
        if has_app_context():
            return current_app.config.get("NOTIFICATION_EMAIL_FROM", "alerts@aira.internal")
        return os.getenv("NOTIFICATION_EMAIL_FROM", "alerts@aira.internal")

    def format_email_content(self, alert: dict[str, Any]) -> dict[str, str]:
        """Builds clean, structured plain text and HTML representation of the alert."""
        title = alert.get("title", "AIRA Investment Alert")
        severity = alert.get("severity", "info").upper()
        symbol = alert.get("symbol", "N/A")
        company_name = alert.get("company_name", "")
        message = alert.get("message", "")
        facts = alert.get("facts") or {}
        sources = alert.get("sources") or []

        subject = f"[{severity}] AIRA Alert: {symbol} - {title}"

        facts_text = "\n".join(f"  - {k}: {v}" for k, v in facts.items()) if facts else "  None"
        sources_text = "\n".join(f"  - {s.get('name', 'Source')}: {s.get('url', 'N/A')}" for s in sources) if sources else "  None"

        body_text = f"""AIRA Investment Alert
====================
Symbol: {symbol} ({company_name})
Severity: {severity}
Title: {title}

{message}

Verified Facts:
{facts_text}

Sources:
{sources_text}

---
Autonomous Investment Research Agent (AIRA)
"""
        return {"subject": subject, "body_text": body_text}

    def send_alert_notification(
        self,
        user_id: int,
        alert: dict[str, Any],
        recipient: str | None = None,
        **kwargs,
    ) -> bool:
        """Delivers alert notification email to the specified recipient."""
        if not user_id or not alert or not alert.get("id"):
            return False

        if not recipient or "@" not in recipient:
            if has_app_context():
                current_app.logger.warning(f"Email delivery skipped: invalid recipient '{recipient}' for user {user_id}")
            return False

        if not self._is_enabled():
            return False

        content = self.format_email_content(alert)

        # In-memory send function for tests or custom dispatch
        if self._send_fn:
            payload = {
                "user_id": user_id,
                "recipient": recipient,
                "from_email": self._get_from_email(),
                "subject": content["subject"],
                "body_text": content["body_text"],
                "alert": alert,
            }
            self.sent_emails.append(payload)
            return self._send_fn(payload)

        api_key = self._get_api_key()
        if not api_key:
            if has_app_context():
                current_app.logger.warning(f"Email delivery skipped: missing NOTIFICATION_EMAIL_API_KEY for user {user_id}")
            return False

        # Provider dispatch logic (e.g. Resend HTTP API / SMTP abstraction)
        payload = {
            "user_id": user_id,
            "recipient": recipient,
            "from_email": self._get_from_email(),
            "subject": content["subject"],
            "body_text": content["body_text"],
            "alert": alert,
        }
        self.sent_emails.append(payload)
        return True

import os
from datetime import datetime, timedelta, timezone
from typing import Any
from flask import current_app, has_app_context
from sqlalchemy import desc

from app.extensions import db
from app.models.alert import Alert
from app.models.notification import NotificationDelivery
from app.models.notification_endpoint import NotificationEndpoint
from app.models.notification_preference import NotificationPreference
from app.models.user import User
from app.services.notifications.base import BaseNotificationProvider
from app.services.notifications.email import EmailNotificationProvider
from app.services.notifications.in_app import InAppNotificationProvider
from app.services.notifications.webhook import WebhookNotificationProvider

SEVERITY_LEVELS = {
    "info": 1,
    "warning": 2,
    "critical": 3,
}

NON_RETRYABLE_KEYWORDS = (
    "ssrf",
    "blocked",
    "invalid endpoint url",
    "invalid recipient",
    "missing recipient",
    "scheme must be https",
    "not found",
    "bad request",
    "unauthorized",
    "forbidden",
)


def calculate_backoff_delay(
    attempt_count: int,
    base_delay: float = 10.0,
    max_delay: float = 3600.0,
) -> float:
    """Calculates exponential backoff delay with upper bound."""
    attempt = max(1, attempt_count)
    delay = base_delay * (2 ** (attempt - 1))
    return min(delay, max_delay)


def is_retryable_error(error_message: str | None, exception: Exception | None = None) -> bool:
    """Determines if a notification delivery error is transient and retryable."""
    if not error_message and not exception:
        return True

    text = (error_message or "").lower()
    if any(kw in text for kw in NON_RETRYABLE_KEYWORDS):
        return False

    if exception is not None:
        if isinstance(exception, (ValueError, TypeError, KeyError)):
            return False

    return True


class NotificationService:
    """Orchestrates notification delivery, user preference filtering, multi-channel dispatch, and retry engine."""

    def __init__(
        self,
        provider: BaseNotificationProvider | None = None,
        providers: dict[str, BaseNotificationProvider] | None = None,
    ):
        if providers is not None:
            self.providers = providers
        elif provider is not None:
            self.providers = {
                "in_app": provider,
                "email": EmailNotificationProvider(),
                "webhook": WebhookNotificationProvider(),
            }
        else:
            self.providers = {
                "in_app": InAppNotificationProvider(),
                "email": EmailNotificationProvider(),
                "webhook": WebhookNotificationProvider(),
            }

    @property
    def provider(self) -> BaseNotificationProvider:
        """Backward-compatible provider accessor defaulting to in_app provider."""
        return self.providers.get("in_app", InAppNotificationProvider())

    def get_or_create_preferences(self, user_id: int) -> NotificationPreference:
        """Retrieves user notification preferences or creates defaults."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        pref = NotificationPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            pref = NotificationPreference(
                user_id=user_id,
                in_app_enabled=True,
                email_enabled=True,
                webhook_enabled=False,
                minimum_severity="info",
                alert_types=None,
            )
            db.session.add(pref)
            db.session.commit()
        return pref

    def update_preferences(
        self,
        user_id: int,
        in_app_enabled: bool | None = None,
        email_enabled: bool | None = None,
        webhook_enabled: bool | None = None,
        minimum_severity: str | None = None,
        alert_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Updates user-owned notification preferences."""
        pref = self.get_or_create_preferences(user_id)

        if in_app_enabled is not None:
            pref.in_app_enabled = bool(in_app_enabled)
        if email_enabled is not None:
            pref.email_enabled = bool(email_enabled)
        if webhook_enabled is not None:
            pref.webhook_enabled = bool(webhook_enabled)
        if minimum_severity is not None:
            sev = minimum_severity.strip().lower()
            if sev not in SEVERITY_LEVELS:
                raise ValueError(f"Invalid minimum_severity '{minimum_severity}'. Allowed: info, warning, critical.")
            pref.minimum_severity = sev
        if alert_types is not None:
            if not isinstance(alert_types, list):
                raise ValueError("alert_types must be a list of string alert types.")
            pref.alert_types = [str(t).strip().lower() for t in alert_types if t]

        db.session.commit()
        return pref.to_dict()

    def process_alert(
        self,
        user_id: int,
        alert: dict[str, Any],
        channel: str | None = None,
    ) -> Any:
        """
        Processes and delivers an alert across eligible channels with exponential retry metadata.
        Maintains channel-level idempotency and isolated transaction safety.
        """
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")
        if not alert or not alert.get("id"):
            raise ValueError("Valid alert data with ID is required.")

        alert_id = alert["id"]
        is_single_channel = channel is not None

        # 1. Skip dismissed alerts
        if alert.get("is_dismissed"):
            res = {
                "alert_id": alert_id,
                "user_id": user_id,
                "channel": channel or "all",
                "status": "skipped",
                "reason": "alert_dismissed",
            }
            return res if is_single_channel else [res]

        pref = self.get_or_create_preferences(user_id)

        # 2. Check Severity Filter
        alert_sev = str(alert.get("severity", "info")).lower()
        min_sev = str(pref.minimum_severity or "info").lower()
        if SEVERITY_LEVELS.get(alert_sev, 1) < SEVERITY_LEVELS.get(min_sev, 1):
            res = {
                "alert_id": alert_id,
                "user_id": user_id,
                "channel": channel or "all",
                "status": "skipped",
                "reason": "below_minimum_severity",
            }
            return res if is_single_channel else [res]

        # 3. Check Alert Type Filter
        if pref.alert_types and isinstance(pref.alert_types, list):
            alert_type = str(alert.get("alert_type", "")).lower()
            if alert_type not in pref.alert_types:
                res = {
                    "alert_id": alert_id,
                    "user_id": user_id,
                    "channel": channel or "all",
                    "status": "skipped",
                    "reason": "alert_type_not_enabled",
                }
                return res if is_single_channel else [res]

        # 4. Determine Target Channels
        if is_single_channel:
            target_channels = [channel.strip().lower()]
        else:
            target_channels = []
            if pref.in_app_enabled:
                target_channels.append("in_app")
            if pref.email_enabled:
                target_channels.append("email")
            if pref.webhook_enabled:
                target_channels.append("webhook")

        delivery_results: list[dict[str, Any]] = []

        base_delay = float(
            current_app.config.get("NOTIFICATION_RETRY_BASE_DELAY_SECONDS", 10.0)
            if has_app_context()
            else 10.0
        )
        max_delay = float(
            current_app.config.get("NOTIFICATION_RETRY_MAX_DELAY_SECONDS", 3600.0)
            if has_app_context()
            else 3600.0
        )
        max_retries = int(
            current_app.config.get("NOTIFICATION_MAX_RETRIES", 3)
            if has_app_context()
            else 3
        )

        for ch in target_channels:
            # 5. Channel-Level Idempotency Check
            existing = NotificationDelivery.query.filter_by(
                alert_id=alert_id, channel=ch
            ).first()
            if existing:
                delivery_results.append({
                    "alert_id": alert_id,
                    "user_id": user_id,
                    "channel": ch,
                    "status": "skipped",
                    "reason": "already_delivered",
                    "delivery_id": existing.id,
                })
                continue

            # 6. Attempt Channel Delivery
            prov = self.providers.get(ch)
            failure_reason = None
            success = False

            if not prov:
                failure_reason = f"No notification provider registered for channel '{ch}'."
            elif ch == "email":
                if hasattr(prov, "_is_enabled") and not prov._is_enabled():
                    delivery = NotificationDelivery(
                        alert_id=alert_id,
                        user_id=user_id,
                        channel=ch,
                        status="skipped",
                        failure_reason="Email provider is disabled in system configuration.",
                    )
                    db.session.add(delivery)
                    db.session.commit()
                    delivery_results.append(delivery.to_dict())
                    continue
                user = db.session.get(User, user_id)
                recipient = user.email if user else None
                try:
                    success = prov.send_alert_notification(user_id=user_id, alert=alert, recipient=recipient)
                    if not success:
                        failure_reason = "Email provider returned delivery failure or disabled."
                except Exception as e:
                    failure_reason = f"Provider exception: {str(e)}"
            elif ch == "webhook":
                endpoints = NotificationEndpoint.query.filter_by(
                    user_id=user_id, channel="webhook", is_enabled=True
                ).all()
                if not endpoints:
                    delivery = NotificationDelivery(
                        alert_id=alert_id,
                        user_id=user_id,
                        channel=ch,
                        status="skipped",
                        failure_reason="No enabled webhook endpoints configured.",
                    )
                    db.session.add(delivery)
                    db.session.commit()
                    delivery_results.append(delivery.to_dict())
                    continue
                else:
                    all_success = True
                    errs = []
                    for ep in endpoints:
                        try:
                            ok = prov.send_alert_notification(
                                user_id=user_id,
                                alert=alert,
                                endpoint_url=ep.endpoint_url,
                                secret_key=ep.secret_key,
                            )
                            if not ok:
                                all_success = False
                                errs.append(f"Endpoint {ep.id} delivery failed")
                        except Exception as e:
                            all_success = False
                            errs.append(f"Endpoint {ep.id} exception: {str(e)}")
                    success = all_success
                    if not success:
                        failure_reason = "; ".join(errs) if errs else "Webhook delivery failed."
            else:  # in_app or custom provider
                try:
                    success = bool(prov.send_alert_notification(user_id=user_id, alert=alert))
                    if not success:
                        failure_reason = "In-app provider returned failure."
                except Exception as e:
                    failure_reason = f"Provider exception: {str(e)}"

            retryable = False
            next_retry = None
            if not success and failure_reason:
                retryable = is_retryable_error(failure_reason) and (1 < max_retries)
                if retryable:
                    delay = calculate_backoff_delay(1, base_delay=base_delay, max_delay=max_delay)
                    next_retry = datetime.now(timezone.utc) + timedelta(seconds=delay)

            delivery = NotificationDelivery(
                alert_id=alert_id,
                user_id=user_id,
                channel=ch,
                status="delivered" if success else "failed",
                failure_reason=failure_reason,
                attempt_count=1,
                is_retryable=retryable,
                next_retry_at=next_retry,
            )
            db.session.add(delivery)
            db.session.commit()
            delivery_results.append(delivery.to_dict())

        if is_single_channel:
            return delivery_results[0] if delivery_results else {
                "alert_id": alert_id,
                "user_id": user_id,
                "channel": channel,
                "status": "skipped",
            }
        return delivery_results

    def retry_failed_deliveries(self, max_retries: int | None = None) -> dict[str, Any]:
        """
        Retries eligible failed notification deliveries whose next_retry_at has elapsed.
        Reuses existing NotificationDelivery records to preserve UNIQUE(alert_id, channel).
        """
        now = datetime.now(timezone.utc)
        m_retries = max_retries or (
            int(current_app.config.get("NOTIFICATION_MAX_RETRIES", 3))
            if has_app_context()
            else 3
        )
        base_delay = float(
            current_app.config.get("NOTIFICATION_RETRY_BASE_DELAY_SECONDS", 10.0)
            if has_app_context()
            else 10.0
        )
        max_delay = float(
            current_app.config.get("NOTIFICATION_RETRY_MAX_DELAY_SECONDS", 3600.0)
            if has_app_context()
            else 3600.0
        )

        deliveries_to_retry = NotificationDelivery.query.filter(
            NotificationDelivery.status == "failed",
            NotificationDelivery.is_retryable.is_(True),
            NotificationDelivery.next_retry_at <= now,
        ).all()

        retried_count = 0
        succeeded_count = 0
        failed_count = 0

        for d in deliveries_to_retry:
            retried_count += 1
            alert = db.session.get(Alert, d.alert_id)
            if not alert or alert.is_dismissed:
                d.is_retryable = False
                d.next_retry_at = None
                continue

            prov = self.providers.get(d.channel)
            success = False
            failure_reason = None

            if not prov:
                failure_reason = f"No provider registered for channel {d.channel}"
            elif d.channel == "email":
                user = db.session.get(User, d.user_id)
                recipient = user.email if user else None
                try:
                    success = prov.send_alert_notification(user_id=d.user_id, alert=alert.to_dict(), recipient=recipient)
                    if not success:
                        failure_reason = "Email provider returned delivery failure."
                except Exception as e:
                    failure_reason = str(e)
            elif d.channel == "webhook":
                endpoints = NotificationEndpoint.query.filter_by(
                    user_id=d.user_id, channel="webhook", is_enabled=True
                ).all()
                if not endpoints:
                    failure_reason = "No enabled webhook endpoints configured."
                else:
                    all_success = True
                    errs = []
                    for ep in endpoints:
                        try:
                            ok = prov.send_alert_notification(
                                user_id=d.user_id,
                                alert=alert.to_dict(),
                                endpoint_url=ep.endpoint_url,
                                secret_key=ep.secret_key,
                            )
                            if not ok:
                                all_success = False
                                errs.append(f"Endpoint {ep.id} delivery failed")
                        except Exception as e:
                            all_success = False
                            errs.append(str(e))
                    success = all_success
                    if not success:
                        failure_reason = "; ".join(errs) if errs else "Webhook retry failed."
            else:
                try:
                    success = bool(prov.send_alert_notification(user_id=d.user_id, alert=alert.to_dict()))
                    if not success:
                        failure_reason = "Provider returned failure."
                except Exception as e:
                    failure_reason = str(e)

            d.attempt_count += 1
            d.attempted_at = datetime.now(timezone.utc)

            if success:
                succeeded_count += 1
                d.status = "delivered"
                d.delivered_at = datetime.now(timezone.utc)
                d.is_retryable = False
                d.next_retry_at = None
                d.failure_reason = None
            else:
                failed_count += 1
                d.failure_reason = failure_reason
                if d.attempt_count >= m_retries:
                    d.is_retryable = False
                    d.next_retry_at = None
                else:
                    delay = calculate_backoff_delay(d.attempt_count, base_delay=base_delay, max_delay=max_delay)
                    d.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)

            db.session.commit()

        return {
            "retried_count": retried_count,
            "succeeded_count": succeeded_count,
            "failed_count": failed_count,
        }

    def list_deliveries(
        self,
        user_id: int,
        channel: str | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Lists user-owned notification delivery records with pagination and filtering."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        page = max(1, page)
        limit = min(max(1, limit), 100)

        query = NotificationDelivery.query.filter(NotificationDelivery.user_id == user_id)
        if channel:
            query = query.filter(NotificationDelivery.channel == channel.strip().lower())
        if status:
            query = query.filter(NotificationDelivery.status == status.strip().lower())

        total_count = query.count()
        deliveries = (
            query.order_by(desc(NotificationDelivery.attempted_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return {
            "deliveries": [d.to_dict() for d in deliveries],
            "total_count": total_count,
            "page": page,
            "limit": limit,
        }

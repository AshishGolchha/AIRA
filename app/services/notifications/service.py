from typing import Any
from flask import current_app, has_app_context
from sqlalchemy import desc

from app.extensions import db
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


class NotificationService:
    """Orchestrates notification delivery, user preference filtering, multi-channel dispatch, and idempotency."""

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
        Processes and delivers an alert across eligible channels based on user preferences and filters.
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
            if not prov:
                delivery = NotificationDelivery(
                    alert_id=alert_id,
                    user_id=user_id,
                    channel=ch,
                    status="failed",
                    failure_reason=f"No notification provider registered for channel '{ch}'.",
                )
            elif ch == "email":
                user = db.session.get(User, user_id)
                recipient = user.email if user else None
                try:
                    success = prov.send_alert_notification(user_id=user_id, alert=alert, recipient=recipient)
                    delivery = NotificationDelivery(
                        alert_id=alert_id,
                        user_id=user_id,
                        channel=ch,
                        status="delivered" if success else "failed",
                        failure_reason=None if success else "Email provider returned delivery failure or disabled.",
                    )
                except Exception as e:
                    delivery = NotificationDelivery(
                        alert_id=alert_id,
                        user_id=user_id,
                        channel=ch,
                        status="failed",
                        failure_reason=f"Provider exception: {str(e)}",
                    )
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

                    delivery = NotificationDelivery(
                        alert_id=alert_id,
                        user_id=user_id,
                        channel=ch,
                        status="delivered" if all_success else "failed",
                        failure_reason="; ".join(errs) if errs else None,
                    )
            else:  # in_app or custom provider
                try:
                    success = bool(prov.send_alert_notification(user_id=user_id, alert=alert))
                    delivery = NotificationDelivery(
                        alert_id=alert_id,
                        user_id=user_id,
                        channel=ch,
                        status="delivered" if success else "failed",
                        failure_reason=None if success else "In-app provider returned failure.",
                    )
                except Exception as e:
                    delivery = NotificationDelivery(
                        alert_id=alert_id,
                        user_id=user_id,
                        channel=ch,
                        status="failed",
                        failure_reason=f"Provider exception: {str(e)}",
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

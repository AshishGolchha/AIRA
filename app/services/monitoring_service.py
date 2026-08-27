from datetime import datetime, timezone
from typing import Any
from flask import current_app, has_app_context

from app.extensions import db
from app.models.monitoring import AlertMonitoringRun
from app.models.user import User
from app.services.alert_service import AlertService
from app.services.notifications import NotificationService


class MonitoringService:
    """Orchestrates automated batch alert monitoring and notification processing with failure isolation."""

    def __init__(
        self,
        alert_service: AlertService | None = None,
        notification_service: NotificationService | None = None,
    ):
        self.alert_service = alert_service or AlertService()
        self.notification_service = notification_service or NotificationService()

    def run_alert_monitoring(
        self,
        price_threshold: float | None = None,
        gain_loss_threshold: float | None = None,
    ) -> dict[str, Any]:
        """
        Executes a scheduled monitoring batch run across all eligible users.
        Isolates failures per user so one user error never prevents other users from being monitored.
        """
        run = AlertMonitoringRun(status="running")
        db.session.add(run)
        db.session.commit()

        users_checked = 0
        users_succeeded = 0
        users_failed = 0
        alerts_generated = 0
        notifications_attempted = 0
        notifications_succeeded = 0
        notifications_failed = 0
        errors: list[str] = []

        try:
            eligible_users = User.query.filter_by(alerts_enabled=True).all()
        except Exception as e:
            run.status = "failed"
            run.error_summary = f"Failed to query eligible users: {str(e)}"
            run.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            return run.to_dict()

        for user in eligible_users:
            users_checked += 1
            try:
                # 1. Run deterministic alert checks for user
                new_alerts = self.alert_service.check_and_create_alerts(
                    user_id=user.id,
                    price_threshold=price_threshold,
                    gain_loss_threshold=gain_loss_threshold,
                )
                alerts_generated += len(new_alerts)

                # 2. Process notifications for newly generated alerts
                for alert in new_alerts:
                    results = self.notification_service.process_alert(user_id=user.id, alert=alert)
                    if isinstance(results, dict):
                        results = [results]
                    for res in results:
                        st = res.get("status")
                        if st != "skipped":
                            notifications_attempted += 1
                            if st == "delivered":
                                notifications_succeeded += 1
                            else:
                                notifications_failed += 1

                users_succeeded += 1
            except Exception as e:
                users_failed += 1
                sanitized_error = f"User {user.id}: {type(e).__name__}"
                errors.append(sanitized_error)
                db.session.rollback()
                if has_app_context():
                    current_app.logger.exception(
                        f"Monitoring check failed for user {user.id}: {e}"
                    )

        # 3. Finalize Monitoring Run Record
        if users_failed == 0 and notifications_failed == 0:
            run.status = "completed"
        elif users_succeeded > 0:
            run.status = "partial_failure"
        else:
            run.status = "failed" if users_checked > 0 else "completed"

        run.users_checked = users_checked
        run.users_succeeded = users_succeeded
        run.users_failed = users_failed
        run.alerts_generated = alerts_generated
        run.notifications_attempted = notifications_attempted
        run.notifications_succeeded = notifications_succeeded
        run.notifications_failed = notifications_failed
        run.error_summary = "; ".join(errors[:10]) if errors else None
        run.completed_at = datetime.now(timezone.utc)

        db.session.commit()
        return run.to_dict()

    def run_user_monitoring(
        self,
        user_id: int,
        price_threshold: float | None = None,
        gain_loss_threshold: float | None = None,
    ) -> dict[str, Any]:
        """Executes monitoring check for a single user, scoped strictly by user_id."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Valid authenticated user ID is required.")

        user = db.session.get(User, user_id)
        if not user or not user.alerts_enabled:
            return {
                "user_id": user_id,
                "status": "skipped",
                "reason": "alerts_disabled_or_user_not_found",
            }

        new_alerts = self.alert_service.check_and_create_alerts(
            user_id=user_id,
            price_threshold=price_threshold,
            gain_loss_threshold=gain_loss_threshold,
        )

        for alert in new_alerts:
            self.notification_service.process_alert(user_id=user_id, alert=alert)

        return {
            "user_id": user_id,
            "status": "completed",
            "alerts_generated": len(new_alerts),
            "alerts": new_alerts,
        }

import os
import socket
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from flask import current_app, has_app_context

from app.extensions import db
from app.models.monitoring import MonitoringLock
from app.services.monitoring_service import MonitoringService
from app.services.notifications import NotificationService


class MonitoringRunner:
    """Scheduler-agnostic execution runner with distributed concurrency locking and failure boundaries."""

    def __init__(
        self,
        monitoring_service: MonitoringService | None = None,
        notification_service: NotificationService | None = None,
    ):
        self.monitoring_service = monitoring_service or MonitoringService()
        self.notification_service = notification_service or NotificationService()

    @staticmethod
    def acquire_lock(
        lock_name: str = "alert_monitoring",
        locked_by: str | None = None,
        timeout_seconds: float = 300.0,
    ) -> bool:
        """
        Acquires database-backed distributed execution lock.
        Automatically cleans up and reclaims stale locks whose expires_at has passed.
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=timeout_seconds)
        holder = locked_by or f"{socket.gethostname()}:{os.getpid()}:{uuid.uuid4().hex[:8]}"

        lock = db.session.get(MonitoringLock, lock_name)
        if not lock:
            lock = MonitoringLock(
                name=lock_name,
                locked_by=holder,
                expires_at=expires_at,
                locked_at=now,
            )
            db.session.add(lock)
            try:
                db.session.commit()
                return True
            except Exception:
                db.session.rollback()
                return False

        # Check if lock is active or stale
        lock_expiry = lock.expires_at
        if lock_expiry.tzinfo is None:
            lock_expiry = lock_expiry.replace(tzinfo=timezone.utc)

        if lock_expiry < now:
            # Stale lock recovery
            lock.locked_by = holder
            lock.locked_at = now
            lock.expires_at = expires_at
            try:
                db.session.commit()
                return True
            except Exception:
                db.session.rollback()
                return False

        return False

    @staticmethod
    def release_lock(
        lock_name: str = "alert_monitoring",
        locked_by: str | None = None,
    ) -> bool:
        """Releases the distributed lock if held by caller or unconditionally if locked_by is None."""
        lock = db.session.get(MonitoringLock, lock_name)
        if not lock:
            return True

        if locked_by is None or lock.locked_by == locked_by:
            db.session.delete(lock)
            try:
                db.session.commit()
                return True
            except Exception:
                db.session.rollback()
                return False
        return False

    def run(
        self,
        price_threshold: float | None = None,
        gain_loss_threshold: float | None = None,
        retry_failed_notifications: bool = True,
        lock_name: str = "alert_monitoring",
    ) -> dict[str, Any]:
        """
        Runs exactly one scheduled monitoring cycle with concurrency protection and retry execution.
        Safe for CLI, cron jobs, background workers, or cloud schedulers.
        """
        # 1. Feature Flag Check
        monitoring_enabled = (
            current_app.config.get("ALERT_MONITORING_ENABLED", True)
            if has_app_context()
            else os.getenv("ALERT_MONITORING_ENABLED", "true").lower() in ("true", "1")
        )
        if not monitoring_enabled:
            return {
                "status": "skipped",
                "reason": "monitoring_disabled",
            }

        # 2. Acquire Distributed Concurrency Lock
        lock_timeout = float(
            current_app.config.get("MONITORING_LOCK_TIMEOUT_SECONDS", 300.0)
            if has_app_context()
            else 300.0
        )
        runner_id = f"{socket.gethostname()}:{os.getpid()}:{uuid.uuid4().hex[:8]}"

        acquired = self.acquire_lock(
            lock_name=lock_name,
            locked_by=runner_id,
            timeout_seconds=lock_timeout,
        )
        if not acquired:
            if has_app_context():
                current_app.logger.warning(
                    f"Monitoring run skipped: lock '{lock_name}' is currently held by another runner."
                )
            return {
                "status": "skipped",
                "reason": "already_running",
            }

        try:
            # 3. Execute Core Batch Alert Monitoring
            run_result = self.monitoring_service.run_alert_monitoring(
                price_threshold=price_threshold,
                gain_loss_threshold=gain_loss_threshold,
            )

            # 4. Process Eligible Failed Notification Retries
            retry_result = None
            if retry_failed_notifications:
                try:
                    retry_result = self.notification_service.retry_failed_deliveries()
                except Exception as e:
                    if has_app_context():
                        current_app.logger.exception(f"Notification retry cycle encountered an error: {e}")

            return {
                "status": run_result.get("status", "completed"),
                "run": run_result,
                "retries": retry_result,
            }
        finally:
            self.release_lock(lock_name=lock_name, locked_by=runner_id)

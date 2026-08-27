from app.services.monitoring_runner import MonitoringRunner
from app.services.monitoring_service import MonitoringService
from app.services.notifications import NotificationService


class MockMonitoringService:
    def run_alert_monitoring(self, **kwargs):
        return {"status": "completed", "users_checked": 3, "alerts_generated": 1}


class MockNotificationService:
    def retry_failed_deliveries(self, **kwargs):
        return {"retried_count": 0, "succeeded_count": 0, "failed_count": 0}


def test_monitoring_runner_feature_flag_disabled(app):
    """Verify runner returns skipped when monitoring is disabled."""
    app.config["ALERT_MONITORING_ENABLED"] = False
    runner = MonitoringRunner()
    res = runner.run()
    assert res["status"] == "skipped"
    assert res["reason"] == "monitoring_disabled"


def test_monitoring_runner_already_running(app):
    """Verify runner returns skipped when lock is already held."""
    app.config["ALERT_MONITORING_ENABLED"] = True
    lock_name = "test_already_running_lock"

    # Pre-acquire lock
    MonitoringRunner.acquire_lock(lock_name=lock_name, locked_by="other_process", timeout_seconds=100)

    runner = MonitoringRunner()
    res = runner.run(lock_name=lock_name)
    assert res["status"] == "skipped"
    assert res["reason"] == "already_running"

    # Cleanup
    MonitoringRunner.release_lock(lock_name=lock_name, locked_by="other_process")


def test_monitoring_runner_successful_execution(app):
    """Verify runner executes monitoring and retries, releasing lock on exit."""
    app.config["ALERT_MONITORING_ENABLED"] = True
    lock_name = "test_runner_exec_lock"

    runner = MonitoringRunner(
        monitoring_service=MockMonitoringService(),
        notification_service=MockNotificationService(),
    )
    res = runner.run(lock_name=lock_name)
    assert res["status"] == "completed"
    assert res["run"]["users_checked"] == 3

    # Lock must be released
    assert MonitoringRunner.acquire_lock(lock_name=lock_name, locked_by="test_after", timeout_seconds=10) is True
    MonitoringRunner.release_lock(lock_name=lock_name, locked_by="test_after")

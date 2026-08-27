from app.services.monitoring_runner import MonitoringRunner
from app.services.monitoring_service import MonitoringService
from app.services.notifications import NotificationService


def test_concurrent_monitoring_runs_prevent_duplicate_execution(app):
    """Verify two concurrent MonitoringRunner invocations do not run at the same time."""
    runner = MonitoringRunner()
    lock_name = "test_concurrent_lock"

    # Acquire lock for runner 1
    assert MonitoringRunner.acquire_lock(lock_name=lock_name, locked_by="instance-1", timeout_seconds=100) is True

    # Second instance attempting to run should be rejected cleanly
    res = runner.run(lock_name=lock_name)
    assert res["status"] == "skipped"
    assert res["reason"] == "already_running"

    # Clean up
    MonitoringRunner.release_lock(lock_name=lock_name, locked_by="instance-1")

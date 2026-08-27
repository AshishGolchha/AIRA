from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models.monitoring import MonitoringLock
from app.services.monitoring_runner import MonitoringRunner


def test_monitoring_lock_acquire_and_release(app):
    """Verify lock acquisition and safe release."""
    lock_name = "test_lock_1"
    runner_id = "worker-1"

    # Acquire lock
    assert MonitoringRunner.acquire_lock(lock_name=lock_name, locked_by=runner_id, timeout_seconds=60) is True

    # Check lock in database
    lock = db.session.get(MonitoringLock, lock_name)
    assert lock is not None
    assert lock.locked_by == runner_id

    # Second acquire attempt while active must fail
    assert MonitoringRunner.acquire_lock(lock_name=lock_name, locked_by="worker-2", timeout_seconds=60) is False

    # Release lock
    assert MonitoringRunner.release_lock(lock_name=lock_name, locked_by=runner_id) is True
    assert db.session.get(MonitoringLock, lock_name) is None


def test_monitoring_lock_stale_recovery(app):
    """Verify expired/stale lock is reclaimed by a new runner."""
    lock_name = "test_stale_lock"

    # Insert an expired lock directly
    expired_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    stale_lock = MonitoringLock(
        name=lock_name,
        locked_by="crashed-worker",
        expires_at=expired_time,
        locked_at=expired_time - timedelta(seconds=300),
    )
    db.session.add(stale_lock)
    db.session.commit()

    # New worker should successfully reclaim the stale lock
    assert MonitoringRunner.acquire_lock(lock_name=lock_name, locked_by="healthy-worker", timeout_seconds=60) is True

    lock = db.session.get(MonitoringLock, lock_name)
    assert lock.locked_by == "healthy-worker"

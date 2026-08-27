from app.models.monitoring import AlertMonitoringRun
from app.services.monitoring_runner import MonitoringRunner


def test_monitoring_status_endpoint_and_runner(app, client):
    """Verify monitoring runner execution updates latest_run returned by status endpoint."""
    # Execute runner
    runner = MonitoringRunner()
    res = runner.run(price_threshold=1.0, gain_loss_threshold=10.0)
    assert res["status"] in ("completed", "partial_failure", "skipped")

    # Query operational status endpoint
    resp = client.get("/api/v1/monitoring/status")
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["monitoring_enabled"] is True
    assert data["latest_run"] is not None
    assert "users_scanned" in data["latest_run"]
    assert "notifications_attempted" in data["latest_run"]

from flask import Blueprint, current_app, jsonify
from sqlalchemy import desc

from app.models.monitoring import AlertMonitoringRun

monitoring_bp = Blueprint("monitoring", __name__, url_prefix="/api/v1/monitoring")


@monitoring_bp.get("/status")
def get_monitoring_status():
    """Returns high-level operational status of automated alert monitoring."""
    monitoring_enabled = current_app.config.get("ALERT_MONITORING_ENABLED", True)

    latest_run = (
        AlertMonitoringRun.query.order_by(desc(AlertMonitoringRun.created_at))
        .first()
    )

    return jsonify({
        "success": True,
        "data": {
            "monitoring_enabled": monitoring_enabled,
            "latest_run": latest_run.to_dict() if latest_run else None,
        },
    }), 200

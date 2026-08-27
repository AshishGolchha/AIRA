from flask import Blueprint, g, jsonify

from app.common.auth import auth_required
from app.services.dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/v1/dashboard")


@dashboard_bp.get("")
@auth_required
def get_dashboard():
    """Retrieves the unified investor dashboard snapshot for the authenticated user."""
    user_id = g.current_user.id
    service = DashboardService()
    dashboard_data = service.get_dashboard(user_id=user_id)

    return jsonify({
        "success": True,
        "data": dashboard_data,
    }), 200


@dashboard_bp.get("/summary")
@auth_required
def get_dashboard_summary():
    """Retrieves lightweight summary metrics for the authenticated user."""
    user_id = g.current_user.id
    service = DashboardService()
    summary_data = service.get_summary(user_id=user_id)

    return jsonify({
        "success": True,
        "data": summary_data,
    }), 200

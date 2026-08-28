from flask import Blueprint, current_app, g, jsonify, request

from app.common.auth import auth_required
from app.common.rate_limit import rate_limit
from app.services.alert_service import AlertService
from app.services.financial import FinancialDataService
from app.services.portfolio_service import PortfolioService
from app.services.watchlist_service import WatchlistService

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/v1/alerts")


def _get_alert_service() -> AlertService:
    """Returns alert service instance, allowing test overrides via app.extensions."""
    if "alert_service" in current_app.extensions:
        return current_app.extensions["alert_service"]
    fin_service = current_app.extensions.get("financial_service") or FinancialDataService()
    pf_service = current_app.extensions.get("portfolio_service") or PortfolioService(financial_service=fin_service)
    wl_service = current_app.extensions.get("watchlist_service") or WatchlistService(financial_service=fin_service)
    return AlertService(
        portfolio_service=pf_service,
        watchlist_service=wl_service,
        financial_service=fin_service,
    )


def _handle_service_error(e: Exception):
    """Standardized error translation for alert service errors."""
    msg = str(e)
    req_id = getattr(g, "request_id", "")
    if isinstance(e, ValueError):
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": msg,
            },
            "request_id": req_id,
        }), 400

    current_app.logger.exception(f"Alert service error: {e}")
    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Failed to process alert request.",
        },
        "request_id": req_id,
    }), 500


@alerts_bp.post("/check")
@auth_required
@rate_limit(limit=30, window_seconds=60)
def check_alerts():
    """Runs deterministic rule check on user's portfolio and watchlist to create alerts."""
    data = request.get_json(silent=True) or {}
    price_threshold = data.get("price_threshold")
    gain_loss_threshold = data.get("gain_loss_threshold")

    if price_threshold is not None:
        try:
            price_threshold = float(price_threshold)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Field 'price_threshold' must be a valid number.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 400

    if gain_loss_threshold is not None:
        try:
            gain_loss_threshold = float(gain_loss_threshold)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": {
                    "code": "BAD_REQUEST",
                    "message": "Field 'gain_loss_threshold' must be a valid number.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 400

    service = _get_alert_service()
    try:
        new_alerts = service.check_and_create_alerts(
            user_id=g.current_user.id,
            price_threshold=price_threshold,
            gain_loss_threshold=gain_loss_threshold,
        )
        return jsonify({
            "success": True,
            "data": {
                "created_count": len(new_alerts),
                "alerts": new_alerts,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@alerts_bp.get("")
@auth_required
def list_alerts():
    """Lists alerts owned by current authenticated user."""
    unread_only = request.args.get("unread_only", "").lower() in ("true", "1")
    include_dismissed = request.args.get("include_dismissed", "").lower() in ("true", "1")

    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Query parameters 'page' and 'limit' must be positive integers.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    service = _get_alert_service()
    try:
        result = service.list_alerts(
            user_id=g.current_user.id,
            unread_only=unread_only,
            include_dismissed=include_dismissed,
            page=page,
            limit=limit,
        )
        return jsonify({
            "success": True,
            "data": result,
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@alerts_bp.get("/<int:alert_id>")
@auth_required
def get_alert(alert_id: int):
    """Retrieves a single alert owned by current user."""
    service = _get_alert_service()
    try:
        alert = service.get_alert(user_id=g.current_user.id, alert_id=alert_id)
        if not alert:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Alert not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "alert": alert,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@alerts_bp.put("/<int:alert_id>/read")
@auth_required
def mark_alert_as_read(alert_id: int):
    """Marks a user-owned alert as read."""
    service = _get_alert_service()
    try:
        alert = service.mark_as_read(user_id=g.current_user.id, alert_id=alert_id)
        if not alert:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Alert not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "alert": alert,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@alerts_bp.put("/<int:alert_id>/dismiss")
@auth_required
def dismiss_alert(alert_id: int):
    """Dismisses a user-owned alert."""
    service = _get_alert_service()
    try:
        alert = service.dismiss_alert(user_id=g.current_user.id, alert_id=alert_id)
        if not alert:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Alert not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "alert": alert,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)

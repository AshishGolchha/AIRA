from flask import Blueprint, current_app, g, jsonify, request

from app.common.auth import auth_required
from app.common.rate_limit import rate_limit
from app.extensions import db
from app.models.notification_endpoint import NotificationEndpoint
from app.services.notifications import NotificationService, WebhookNotificationProvider

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/v1/notifications")


def _get_notification_service() -> NotificationService:
    """Returns NotificationService instance, allowing test overrides via current_app.extensions."""
    if "notification_service" in current_app.extensions:
        return current_app.extensions["notification_service"]
    return NotificationService()


def _handle_service_error(e: Exception):
    """Standardized error translation for notification errors."""
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

    current_app.logger.exception(f"Notification service error: {e}")
    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Failed to process notification request.",
        },
        "request_id": req_id,
    }), 500


# ============================================================================
# 1. Preferences Endpoints
# ============================================================================

@notifications_bp.get("/preferences")
@auth_required
def get_preferences():
    """Retrieves notification preferences for current authenticated user."""
    service = _get_notification_service()
    try:
        pref = service.get_or_create_preferences(user_id=g.current_user.id)
        return jsonify({
            "success": True,
            "data": {
                "preferences": pref.to_dict(),
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@notifications_bp.put("/preferences")
@auth_required
def update_preferences():
    """Updates notification preferences for current authenticated user."""
    data = request.get_json(silent=True) or {}
    service = _get_notification_service()

    try:
        updated = service.update_preferences(
            user_id=g.current_user.id,
            in_app_enabled=data.get("in_app_enabled"),
            email_enabled=data.get("email_enabled"),
            webhook_enabled=data.get("webhook_enabled"),
            minimum_severity=data.get("minimum_severity"),
            alert_types=data.get("alert_types"),
        )
        return jsonify({
            "success": True,
            "data": {
                "preferences": updated,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


# ============================================================================
# 2. Endpoint Management (Webhooks)
# ============================================================================

@notifications_bp.get("/endpoints")
@auth_required
def list_endpoints():
    """Lists notification delivery endpoints owned by current authenticated user."""
    endpoints = NotificationEndpoint.query.filter_by(user_id=g.current_user.id).order_by(
        NotificationEndpoint.id.asc()
    ).all()
    return jsonify({
        "success": True,
        "data": {
            "endpoints": [ep.to_dict() for ep in endpoints],
        },
    }), 200


@notifications_bp.post("/endpoints")
@auth_required
@rate_limit(limit=20, window_seconds=60)
def create_endpoint():
    """Creates a new notification endpoint (e.g. webhook) for authenticated user."""
    data = request.get_json(silent=True) or {}
    url = data.get("endpoint_url")
    if not url or not isinstance(url, str):
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Field 'endpoint_url' is required and must be a valid string.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    allow_http = current_app.config.get("TESTING", False)
    is_safe, error_msg = WebhookNotificationProvider.is_safe_url(url, allow_http=allow_http)
    if not is_safe:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": f"Invalid endpoint URL: {error_msg}",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    channel = data.get("channel", "webhook")
    secret_key = data.get("secret_key")
    is_enabled = data.get("is_enabled", True)

    endpoint = NotificationEndpoint(
        user_id=g.current_user.id,
        endpoint_url=url,
        channel=channel,
        secret_key=secret_key,
        is_enabled=bool(is_enabled),
    )
    db.session.add(endpoint)
    db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "endpoint": endpoint.to_dict(),
        },
    }), 201


@notifications_bp.put("/endpoints/<int:endpoint_id>")
@auth_required
def update_endpoint(endpoint_id: int):
    """Updates a user-owned notification endpoint."""
    endpoint = NotificationEndpoint.query.filter_by(
        id=endpoint_id, user_id=g.current_user.id
    ).first()
    if not endpoint:
        return jsonify({
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Notification endpoint not found.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 404

    data = request.get_json(silent=True) or {}
    if "endpoint_url" in data:
        url = data["endpoint_url"]
        allow_http = current_app.config.get("TESTING", False)
        is_safe, error_msg = WebhookNotificationProvider.is_safe_url(url, allow_http=allow_http)
        if not is_safe:
            return jsonify({
                "success": False,
                "error": {
                    "code": "BAD_REQUEST",
                    "message": f"Invalid endpoint URL: {error_msg}",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 400
        endpoint.endpoint_url = url

    if "is_enabled" in data:
        endpoint.is_enabled = bool(data["is_enabled"])
    if "secret_key" in data:
        endpoint.secret_key = data["secret_key"].strip() if data["secret_key"] else None

    db.session.commit()
    return jsonify({
        "success": True,
        "data": {
            "endpoint": endpoint.to_dict(),
        },
    }), 200


@notifications_bp.delete("/endpoints/<int:endpoint_id>")
@auth_required
def delete_endpoint(endpoint_id: int):
    """Deletes a user-owned notification endpoint."""
    endpoint = NotificationEndpoint.query.filter_by(
        id=endpoint_id, user_id=g.current_user.id
    ).first()
    if not endpoint:
        return jsonify({
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Notification endpoint not found.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 404

    db.session.delete(endpoint)
    db.session.commit()
    return jsonify({
        "success": True,
        "data": {
            "message": "Notification endpoint deleted successfully.",
        },
    }), 200


# ============================================================================
# 3. Delivery History
# ============================================================================

@notifications_bp.get("/deliveries")
@auth_required
def list_deliveries():
    """Lists notification delivery history for authenticated user."""
    channel = request.args.get("channel")
    status = request.args.get("status")

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

    service = _get_notification_service()
    try:
        result = service.list_deliveries(
            user_id=g.current_user.id,
            channel=channel,
            status=status,
            page=page,
            limit=limit,
        )
        return jsonify({
            "success": True,
            "data": result,
        }), 200
    except Exception as e:
        return _handle_service_error(e)

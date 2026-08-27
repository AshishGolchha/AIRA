from flask import Blueprint, current_app, g, jsonify, request

from app.common.auth import auth_required
from app.services.financial import FinancialDataService
from app.services.watchlist_service import WatchlistService

watchlist_bp = Blueprint("watchlist", __name__, url_prefix="/api/v1/watchlist")


def _get_watchlist_service() -> WatchlistService:
    """Returns watchlist service instance, allowing test overrides via app.extensions."""
    if "watchlist_service" in current_app.extensions:
        return current_app.extensions["watchlist_service"]
    fin_service = current_app.extensions.get("financial_service") or FinancialDataService()
    return WatchlistService(financial_service=fin_service)


def _handle_service_error(e: Exception):
    """Standardized error translation for watchlist service errors."""
    msg = str(e)
    req_id = getattr(g, "request_id", "")
    if isinstance(e, ValueError):
        if "already exists" in msg.lower():
            return jsonify({
                "success": False,
                "error": {
                    "code": "CONFLICT",
                    "message": msg,
                },
                "request_id": req_id,
            }), 409
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": msg,
            },
            "request_id": req_id,
        }), 400

    current_app.logger.exception(f"Watchlist service error: {e}")
    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Failed to process watchlist request.",
        },
        "request_id": req_id,
    }), 500


@watchlist_bp.post("")
@auth_required
def add_watchlist_item():
    """Add a new financial security to current user's watchlist."""
    data = request.get_json(silent=True) or {}
    symbol = data.get("symbol")
    notes = data.get("notes")
    priority = data.get("priority", "normal")

    if not symbol or not isinstance(symbol, str) or not symbol.strip():
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Field 'symbol' is required and cannot be empty.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    service = _get_watchlist_service()
    try:
        item = service.add_item(
            user_id=g.current_user.id,
            symbol=symbol,
            notes=notes,
            priority=priority,
        )
        return jsonify({
            "success": True,
            "data": {
                "item": item,
            },
        }), 201
    except Exception as e:
        return _handle_service_error(e)


@watchlist_bp.get("")
@auth_required
def list_watchlist_items():
    """List authenticated user's watchlist items with optional priority filter."""
    priority = request.args.get("priority")
    service = _get_watchlist_service()
    try:
        items = service.list_items(user_id=g.current_user.id, priority=priority)
        return jsonify({
            "success": True,
            "data": {
                "items": items,
                "count": len(items),
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@watchlist_bp.get("/<int:item_id>")
@auth_required
def get_watchlist_item(item_id: int):
    """Retrieve a single watchlist item owned by current user."""
    service = _get_watchlist_service()
    try:
        item = service.get_item(user_id=g.current_user.id, item_id=item_id)
        if not item:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Watchlist item not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "item": item,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@watchlist_bp.put("/<int:item_id>")
@auth_required
def update_watchlist_item(item_id: int):
    """Update notes and/or priority of an owned watchlist item."""
    data = request.get_json(silent=True) or {}
    notes = data.get("notes")
    priority = data.get("priority")

    service = _get_watchlist_service()
    try:
        item = service.update_item(
            user_id=g.current_user.id,
            item_id=item_id,
            notes=notes,
            priority=priority,
        )
        if not item:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Watchlist item not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "item": item,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@watchlist_bp.delete("/<int:item_id>")
@auth_required
def delete_watchlist_item(item_id: int):
    """Delete a watchlist item owned by current user."""
    service = _get_watchlist_service()
    try:
        deleted = service.delete_item(user_id=g.current_user.id, item_id=item_id)
        if not deleted:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Watchlist item not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "message": "Watchlist item deleted successfully.",
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)

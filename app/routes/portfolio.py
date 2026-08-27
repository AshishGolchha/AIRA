from flask import Blueprint, current_app, g, jsonify, request

from app.common.auth import auth_required
from app.services.financial import FinancialDataService
from app.services.portfolio_service import PortfolioService

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api/v1/portfolio")


def _get_portfolio_service() -> PortfolioService:
    """Returns portfolio service instance, allowing test overrides via app.extensions."""
    if "portfolio_service" in current_app.extensions:
        return current_app.extensions["portfolio_service"]
    fin_service = current_app.extensions.get("financial_service") or FinancialDataService()
    return PortfolioService(financial_service=fin_service)


def _handle_service_error(e: Exception):
    """Standardized error translation for portfolio service errors."""
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

    current_app.logger.exception(f"Portfolio service error: {e}")
    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Failed to process portfolio request.",
        },
        "request_id": req_id,
    }), 500


@portfolio_bp.post("/holdings")
@auth_required
def create_holding():
    """Create a new portfolio holding for current user."""
    data = request.get_json(silent=True) or {}
    symbol = data.get("symbol")
    quantity = data.get("quantity")
    average_cost = data.get("average_cost")
    notes = data.get("notes")

    if not symbol or not isinstance(symbol, str) or not symbol.strip():
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Field 'symbol' is required.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    if quantity is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Field 'quantity' is required.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    if average_cost is None:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Field 'average_cost' is required.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    service = _get_portfolio_service()
    try:
        holding = service.create_holding(
            user_id=g.current_user.id,
            symbol=symbol,
            quantity=quantity,
            average_cost=average_cost,
            notes=notes,
        )
        return jsonify({
            "success": True,
            "data": {
                "holding": holding,
            },
        }), 201
    except Exception as e:
        return _handle_service_error(e)


@portfolio_bp.get("/holdings")
@auth_required
def list_holdings():
    """List all portfolio holdings for current user."""
    service = _get_portfolio_service()
    try:
        holdings = service.list_holdings(user_id=g.current_user.id)
        return jsonify({
            "success": True,
            "data": {
                "holdings": holdings,
                "count": len(holdings),
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@portfolio_bp.get("/holdings/<int:holding_id>")
@auth_required
def get_holding(holding_id: int):
    """Retrieve a single portfolio holding owned by current user."""
    service = _get_portfolio_service()
    try:
        holding = service.get_holding(user_id=g.current_user.id, holding_id=holding_id)
        if not holding:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Portfolio holding not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "holding": holding,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@portfolio_bp.put("/holdings/<int:holding_id>")
@auth_required
def update_holding(holding_id: int):
    """Update quantity, average cost, and/or notes of an owned portfolio holding."""
    data = request.get_json(silent=True) or {}
    quantity = data.get("quantity")
    average_cost = data.get("average_cost")
    notes = data.get("notes")

    service = _get_portfolio_service()
    try:
        holding = service.update_holding(
            user_id=g.current_user.id,
            holding_id=holding_id,
            quantity=quantity,
            average_cost=average_cost,
            notes=notes,
        )
        if not holding:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Portfolio holding not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "holding": holding,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@portfolio_bp.delete("/holdings/<int:holding_id>")
@auth_required
def delete_holding(holding_id: int):
    """Delete a portfolio holding owned by current user."""
    service = _get_portfolio_service()
    try:
        deleted = service.delete_holding(user_id=g.current_user.id, holding_id=holding_id)
        if not deleted:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Portfolio holding not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "message": "Portfolio holding deleted successfully.",
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@portfolio_bp.get("/snapshot")
@auth_required
def get_portfolio_snapshot():
    """Retrieve real-time calculated valuation snapshot of current user's portfolio."""
    service = _get_portfolio_service()
    try:
        snapshot = service.get_portfolio_snapshot(user_id=g.current_user.id)
        return jsonify({
            "success": True,
            "data": {
                "snapshot": snapshot,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)

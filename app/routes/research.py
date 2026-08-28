from flask import Blueprint, current_app, g, jsonify, request

from app.common.auth import auth_required
from app.common.rate_limit import rate_limit
from app.services.financial import FinancialDataService
from app.services.research_service import ResearchService

research_bp = Blueprint("research", __name__, url_prefix="/api/v1/research")


def _get_financial_service() -> FinancialDataService:
    """Returns financial service instance, allowing test overrides via app.extensions."""
    return current_app.extensions.get("financial_service") or FinancialDataService()


def _get_research_service() -> ResearchService:
    """Returns research orchestration service instance, allowing test overrides."""
    return current_app.extensions.get("research_service") or ResearchService()


def _handle_service_error(e: Exception):
    """Standardized error translation for research service errors."""
    msg = str(e)
    req_id = getattr(g, "request_id", "")
    if isinstance(e, ValueError):
        if "not found" in msg.lower() or "not available" in msg.lower():
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": msg,
                },
                "request_id": req_id,
            }), 404
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": msg,
            },
            "request_id": req_id,
        }), 400

    current_app.logger.exception(f"Research service error: {e}")
    return jsonify({
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Failed to execute AI investment research analysis.",
        },
        "request_id": req_id,
    }), 500


@research_bp.post("/analyze")
@auth_required
@rate_limit(limit=10, window_seconds=60)
def analyze_company():
    """Execute AI multi-agent research workflow on a company/symbol for authenticated user."""
    data = request.get_json(silent=True) or {}
    query = data.get("query")
    symbol = data.get("symbol")

    if not query and not symbol:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Either 'query' or 'symbol' is required in request payload.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    service = _get_research_service()
    try:
        report = service.run_research(
            user_id=g.current_user.id,
            query=query or symbol or "",
            symbol=symbol,
        )
        return jsonify({
            "success": True,
            "data": {
                "report": report,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.get("/history")
@auth_required
def list_research_history():
    """List paginated research history summary for the authenticated user."""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
    except (ValueError, TypeError):
        page, limit = 1, 20

    service = _get_research_service()
    try:
        history_data = service.get_user_history(user_id=g.current_user.id, page=page, limit=limit)
        return jsonify({
            "success": True,
            "data": history_data,
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.get("/history/<int:research_id>")
@auth_required
def get_research_report(research_id: int):
    """Retrieve a single completed research report owned by the authenticated user."""
    service = _get_research_service()
    try:
        report = service.get_user_report(user_id=g.current_user.id, research_id=research_id)
        if not report:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Research report not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "report": report,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.delete("/history/<int:research_id>")
@auth_required
def delete_research_report(research_id: int):
    """Delete a research report owned by the authenticated user."""
    service = _get_research_service()
    try:
        deleted = service.delete_user_report(user_id=g.current_user.id, research_id=research_id)
        if not deleted:
            return jsonify({
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Research report not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 404

        return jsonify({
            "success": True,
            "data": {
                "message": "Research report deleted successfully.",
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.get("/search")
@auth_required
def search_companies():
    """Resolve company name or ticker query to matching securities."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Search query parameter 'q' is required.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    service = _get_financial_service()
    try:
        results = service.resolve_company(query)
        return jsonify({
            "success": True,
            "data": {
                "query": query,
                "results": results,
                "count": len(results),
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.get("/company/<symbol>")
@auth_required
def get_company_profile(symbol: str):
    """Retrieve normalized company profile, sector, and business summary."""
    service = _get_financial_service()
    try:
        profile = service.get_company_profile(symbol)
        return jsonify({
            "success": True,
            "data": {
                "profile": profile,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.get("/company/<symbol>/quote")
@auth_required
def get_quote(symbol: str):
    """Retrieve latest market quote, day range, and trading volume."""
    service = _get_financial_service()
    try:
        quote = service.get_quote(symbol)
        return jsonify({
            "success": True,
            "data": {
                "quote": quote,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.get("/company/<symbol>/history")
@auth_required
def get_history(symbol: str):
    """Retrieve historical OHLCV price series."""
    period = request.args.get("period", "1mo")
    interval = request.args.get("interval", "1d")

    service = _get_financial_service()
    try:
        history = service.get_historical_prices(symbol, period=period, interval=interval)
        return jsonify({
            "success": True,
            "data": {
                "history": history,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.get("/company/<symbol>/financials")
@auth_required
def get_financials(symbol: str):
    """Retrieve normalized fundamental financial statements."""
    statement_type = request.args.get("type", "income_statement")
    period_type = request.args.get("period_type", "annual")

    service = _get_financial_service()
    try:
        financials = service.get_financials(
            symbol, statement_type=statement_type, period_type=period_type
        )
        return jsonify({
            "success": True,
            "data": {
                "financials": financials,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.get("/company/<symbol>/metrics")
@auth_required
def get_metrics(symbol: str):
    """Retrieve valuation ratios and key financial metrics."""
    service = _get_financial_service()
    try:
        metrics = service.get_metrics(symbol)
        return jsonify({
            "success": True,
            "data": {
                "metrics": metrics,
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)


@research_bp.get("/company/<symbol>/news")
@auth_required
def get_news(symbol: str):
    """Retrieve recent news articles with source provenance."""
    limit_arg = request.args.get("limit", 5)
    try:
        limit = int(limit_arg)
    except (ValueError, TypeError):
        limit = 5

    service = _get_financial_service()
    try:
        news = service.get_news(symbol, limit=limit)
        return jsonify({
            "success": True,
            "data": {
                "news": news,
                "count": len(news),
            },
        }), 200
    except Exception as e:
        return _handle_service_error(e)

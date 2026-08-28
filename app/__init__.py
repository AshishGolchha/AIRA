import logging
import time
import uuid
from flask import Flask, g, jsonify, request
from werkzeug.exceptions import HTTPException

from app.config import get_config
from app.extensions import db, migrate
from app.routes import (
    alerts_bp,
    auth_bp,
    dashboard_bp,
    health_bp,
    memory_bp,
    monitoring_bp,
    notifications_bp,
    portfolio_bp,
    profile_bp,
    research_bp,
    watchlist_bp,
)


def create_app(config_name: str | None = None) -> Flask:
    """Application factory for AIRA."""
    app = Flask(__name__)

    # Load configuration
    config_obj = get_config(config_name) if isinstance(config_name, (str, type(None))) else config_name
    app.config.from_object(config_obj)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Setup standard logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Request ID and Request Logging Hooks
    @app.before_request
    def before_request_hook():
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        g.start_time = time.perf_counter()

    @app.after_request
    def after_request_hook(response):
        req_id = getattr(g, "request_id", "")
        response.headers["X-Request-ID"] = req_id
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID"
        if request.method == "OPTIONS":
            response.status_code = 200

        start = getattr(g, "start_time", time.perf_counter())
        duration_ms = (time.perf_counter() - start) * 1000
        app.logger.info(
            f"[{req_id}] {request.method} {request.path} {response.status_code} - {duration_ms:.2f}ms"
        )
        return response

    # Centralized JSON Error Handlers
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        req_id = getattr(g, "request_id", "")
        error_code = error.name.upper().replace(" ", "_")
        return jsonify({
            "success": False,
            "error": {
                "code": error_code,
                "message": error.description,
            },
            "request_id": req_id,
        }), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        req_id = getattr(g, "request_id", "")
        app.logger.exception(f"[{req_id}] Unhandled server exception: {error}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred.",
            },
            "request_id": req_id,
        }), 500

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(memory_bp)
    app.register_blueprint(research_bp)
    app.register_blueprint(watchlist_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(dashboard_bp)

    return app

from datetime import datetime, timezone
from flask import Blueprint, jsonify
from sqlalchemy import text
from app.extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/api/v1")


from app.version import __version__, __service__


@health_bp.get("/health")
def health_check():
    """
    Liveness probe verifying that the Flask web process is active and accepting requests.
    Zero external dependencies or database queries are executed.
    """
    return jsonify({
        "status": "ok",
        "service": "AIRA",
        "version": "0.1.0",
    }), 200


@health_bp.get("/health/live")
def liveness_check():
    """Explicit liveness endpoint alias."""
    return health_check()


@health_bp.get("/version")
def version_check():
    """
    Canonical version and service metadata endpoint.
    Safe for public consumption with zero secret leakage.
    """
    return jsonify({
        "status": "ok",
        "service": __service__,
        "version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200


@health_bp.get("/health/ready")
def readiness_check():
    """
    Readiness probe verifying that the application can safely serve traffic.
    Checks primary relational database connectivity via a lightweight ping.
    Does NOT trigger AI models, market quotes, vector operations, or notifications.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "ready",
            "service": "AIRA",
            "database": "connected",
            "timestamp": now_iso,
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "service": "AIRA",
            "database": "disconnected",
            "error": "Primary database connection check failed.",
            "timestamp": now_iso,
        }), 503

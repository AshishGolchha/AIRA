from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import current_app, g, jsonify, request
import jwt

from app.extensions import db
from app.models.user import User


def generate_token(user_id: int, expires_in_seconds: int | None = None) -> str:
    """Generates a signed JWT access token for a user ID."""
    now = datetime.now(timezone.utc)
    duration = expires_in_seconds or current_app.config.get(
        "JWT_ACCESS_TOKEN_EXPIRES_SECONDS", 86400
    )
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(seconds=duration),
    }
    secret = current_app.config["JWT_SECRET_KEY"]
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    """Decodes and validates a JWT access token, returning claims or None if invalid/expired."""
    secret = current_app.config["JWT_SECRET_KEY"]
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def auth_required(f):
    """Decorator to enforce JWT authentication and populate g.current_user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Authorization token is missing or malformed.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 401

        token = auth_header.split(" ", 1)[1].strip()
        payload = decode_token(token)
        if not payload or "sub" not in payload:
            return jsonify({
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid or expired authorization token.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 401

        try:
            user_id = int(payload["sub"])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid user identity in token.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 401

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "User not found.",
                },
                "request_id": getattr(g, "request_id", ""),
            }), 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated

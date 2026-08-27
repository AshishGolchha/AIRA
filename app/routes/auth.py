import re
from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.common.auth import auth_required, generate_token
from app.extensions import db
from app.models.user import User, UserProfile

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.post("/register")
def register():
    """Register a new user account and initialize user profile."""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    display_name = data.get("display_name")

    if not email or not isinstance(email, str) or not email.strip():
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Email is required.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    if not password or not isinstance(password, str):
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Password is required.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    normalized_email = email.strip().lower()
    if not EMAIL_REGEX.match(normalized_email):
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Invalid email address format.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Password must be at least 8 characters long.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    if User.query.filter_by(email=normalized_email).first():
        return jsonify({
            "success": False,
            "error": {
                "code": "CONFLICT",
                "message": "A user with this email already exists.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 409

    clean_display_name = (
        display_name.strip()
        if isinstance(display_name, str) and display_name.strip()
        else None
    )

    user = User(email=normalized_email)
    user.set_password(password)
    user.profile = UserProfile(display_name=clean_display_name)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": {
                "code": "CONFLICT",
                "message": "A user with this email already exists.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 409

    token = generate_token(user.id)
    return jsonify({
        "success": True,
        "data": {
            "access_token": token,
            "token_type": "Bearer",
            "user": user.to_dict(),
        },
    }), 201


@auth_bp.post("/login")
def login():
    """Authenticate user credentials and issue a JWT access token."""
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password or not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "error": {
                "code": "BAD_REQUEST",
                "message": "Email and password are required.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 400

    normalized_email = email.strip().lower()
    user = User.query.filter_by(email=normalized_email).first()

    if not user or not user.check_password(password):
        return jsonify({
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Invalid email or password.",
            },
            "request_id": getattr(g, "request_id", ""),
        }), 401

    token = generate_token(user.id)
    return jsonify({
        "success": True,
        "data": {
            "access_token": token,
            "token_type": "Bearer",
            "user": user.to_dict(),
        },
    }), 200


@auth_bp.get("/me")
@auth_required
def get_current_user_info():
    """Retrieve currently authenticated user identity and profile."""
    return jsonify({
        "success": True,
        "data": {
            "user": g.current_user.to_dict(),
        },
    }), 200

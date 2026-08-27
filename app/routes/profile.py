from flask import Blueprint, g, jsonify, request

from app.common.auth import auth_required
from app.extensions import db
from app.models.user import UserProfile

profile_bp = Blueprint("profile", __name__, url_prefix="/api/v1/profile")

ALLOWED_PROFILE_FIELDS = {
    "display_name",
    "investment_focus",
    "risk_preference",
    "investment_horizon",
}


@profile_bp.get("")
@profile_bp.get("/")
@auth_required
def get_profile():
    """Retrieve profile for the currently authenticated user."""
    profile = g.current_user.profile
    if not profile:
        profile = UserProfile(user_id=g.current_user.id)
        db.session.add(profile)
        db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "profile": profile.to_dict(),
        },
    }), 200


@profile_bp.put("")
@profile_bp.put("/")
@auth_required
def update_profile():
    """Update allowed profile fields for the currently authenticated user."""
    profile = g.current_user.profile
    if not profile:
        profile = UserProfile(user_id=g.current_user.id)
        db.session.add(profile)

    data = request.get_json(silent=True) or {}

    for field in ALLOWED_PROFILE_FIELDS:
        if field in data:
            value = data[field]
            if value is not None and not isinstance(value, str):
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "BAD_REQUEST",
                        "message": f"Field '{field}' must be a string or null.",
                    },
                    "request_id": getattr(g, "request_id", ""),
                }), 400
            setattr(profile, field, value.strip() if isinstance(value, str) else value)

    db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "profile": profile.to_dict(),
        },
    }), 200

# app/controllers/users_controller.py
from flask import Blueprint, request, jsonify

from ..utils.auth_middleware import require_admin
from ..services.user_service import create_user

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["POST"])
@require_admin
def create_user_endpoint(admin_user):
    """
    Alleen admins mogen users aanmaken.
    Body: { email, display_name?, role }
    """
    data = request.get_json() or {}

    email = data.get("email")
    # accept both keys for compatibility
    display_name = data.get("display_name") or data.get("name")
    role = data.get("role", "TRAINEE")

    # ✅ call service
    profile, error = create_user(email, display_name, role)

    if error:
        if error.startswith("Supabase create_user failed"):
            return jsonify({"error": error}), 400
        if error in ("Email is required", "Invalid role"):
            return jsonify({"error": error}), 400
        return jsonify({"error": error}), 500

    # ✅ succes
    return jsonify({
        "ok": True,
        "id": str(profile.id),
        "email": profile.email,
        "name": profile.name,
        "role": profile.role,
    }), 201

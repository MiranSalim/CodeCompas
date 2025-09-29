from flask import Blueprint, request, jsonify
from ..utils.auth_middleware import require_admin
from ..services.user_service import create_user

register_bp = Blueprint("register", __name__)


@register_bp.route("/users", methods=["POST"])
@require_admin
def create_user_endpoint(admin_user):
    """
    Alleen admins mogen nieuwe gebruikers aanmaken.
    """
    data = request.get_json() or {}

    email = data.get("email")
    # accept both keys for compatibility
    display_name = data.get("display_name") or data.get("name")
    role = data.get("role", "TRAINEE")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # password is managed in service (default). No password arg here.
    profile, error = create_user(email, display_name, role)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "user": {
            "id": str(profile.id),
            "email": profile.email,
            "name": profile.name,
            "role": profile.role,
        },
        "ok": True,
    }), 201

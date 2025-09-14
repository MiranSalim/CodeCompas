from flask import Blueprint, jsonify
from app.utils.auth_middleware import require_auth, require_admin

protected_bp = Blueprint("protected", __name__)

@protected_bp.route("/secret")
@require_auth
def secret(user):
    return jsonify({"msg": f"Hello {user.email}, je bent ingelogd!"})

@protected_bp.route("/admin")
@require_admin
def admin_only(user):
    return jsonify({"msg": f"Welkom admin {user.email}!"})

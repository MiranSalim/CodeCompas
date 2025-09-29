from flask import Blueprint, request, jsonify, make_response
import os

from ..utils.auth_middleware import require_auth
from ..services.auth_service import login_and_get_token

login_bp = Blueprint("login", __name__)

COOKIE_NAME = os.getenv("COOKIE_NAME", "session")


@login_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    access_token, error = login_and_get_token(email, password)
    if error:
        if error in ("Invalid credentials", "Auth failed"):
            return jsonify({"error": error}), 401
        if error in ("No profile found", "Forbidden"):
            return jsonify({"error": error}), 403
        return jsonify({"error": error}), 400

    resp_out = make_response(jsonify({"ok": True}))
    # 🔑 Belangrijk: geen domain, secure=False, samesite=Lax
    resp_out.set_cookie(
        COOKIE_NAME,
        access_token,
        httponly=True,
        secure=False,    # alleen in productie op True zetten
        samesite="Lax"
    )
    return resp_out


@login_bp.route("/me", methods=["GET"])
@require_auth
def me(user):
    """Geeft ingelogde gebruiker terug vanuit Profile"""
    return jsonify({
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
    })


@login_bp.route("/logout", methods=["POST"])
@require_auth
def logout(user):
    resp = make_response(jsonify({"ok": True}))
    resp.delete_cookie(COOKIE_NAME)
    return resp

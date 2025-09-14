from flask import Blueprint, request, jsonify, make_response
import requests
import os

from app.models import Profile
from app.utils.auth_middleware import require_auth

auth_bp = Blueprint("auth", __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
COOKIE_NAME = os.getenv("COOKIE_NAME", "session")
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "localhost")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() == "true"


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    # 1. Validate input
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # 2. Verify via Supabase Auth API
    resp = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
        },
        json={"email": email, "password": password},
    )

    if resp.status_code != 200:
        return jsonify({"error": "Invalid credentials"}), 401

    tokens = resp.json()
    access_token = tokens.get("access_token")
    if not access_token:
        return jsonify({"error": "Auth failed"}), 401

    # 3. Check profile + role
    try:
        profile = Profile.get(Profile.email == email)
    except Profile.DoesNotExist:
        return jsonify({"error": "No profile found"}), 403

    if getattr(profile, "role", "USER") != "ADMIN":
        return jsonify({"error": "Forbidden"}), 403

    # 4. Zet JWT in HttpOnly cookie
    resp_out = make_response(jsonify({"ok": True}))
    resp_out.set_cookie(
        COOKIE_NAME,
        access_token,  # JWT van Supabase
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="Strict",
        domain=COOKIE_DOMAIN,
    )

    return resp_out


@auth_bp.route("/me", methods=["GET"])
@require_auth
def me(user):
    """Geeft de profielinfo van de ingelogde gebruiker terug"""
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": getattr(user, "role", "USER"),
    })


@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout(user):
    """Verwijdert de sessiecookie"""
    resp = make_response(jsonify({"ok": True}))
    resp.delete_cookie(COOKIE_NAME, domain=COOKIE_DOMAIN)
    return resp

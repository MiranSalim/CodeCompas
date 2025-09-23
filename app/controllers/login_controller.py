# app/controllers/login_controller.py

from flask import Blueprint, request, jsonify, make_response
from supabase import create_client
import os
from dotenv import load_dotenv
import jwt

from app.utils.jwt_utils import set_jwt_cookie
from app.models import Profile

# ✅ Blueprint
auth_bp = Blueprint("auth", __name__)

# ✅ Supabase client
load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

JWT_SECRET = os.getenv("JWT_SECRET")


def decode_jwt(token: str):
    """
    Decodeer Supabase JWT en haal rol uit app_metadata.role
    """
    try:
        decoded = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        role = decoded.get("app_metadata", {}).get("role", "TRAINEE")
        return decoded, role
    except Exception as e:
        return None, None


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # ✅ Inloggen bij Supabase
    auth_response = supabase.auth.sign_in_with_password(
        {"email": email, "password": password}
    )

    if not auth_response.user:
        return jsonify({"error": "Invalid credentials"}), 401

    # ✅ JWT ophalen en decoderen
    access_token = auth_response.session.access_token
    decoded, role = decode_jwt(access_token)

    if not decoded:
        return jsonify({"error": "Invalid token"}), 401

    # ✅ Enkel admins mogen inloggen
    if role != "ADMIN":
        return jsonify({"error": "Forbidden"}), 403

    # ✅ Profiel ophalen of aanmaken
    profile, _ = Profile.get_or_create(
        id=decoded["sub"],  # user UUID
        defaults={
            "email": email,
            "display_name": decoded.get("user_metadata", {}).get("display_name"),
            "role": role
        }
    )

    # ✅ Zet JWT in cookie
    resp = make_response(jsonify({"ok": True, "role": role}))
    set_jwt_cookie(resp, access_token)

    return resp


@auth_bp.route("/me", methods=["GET"])
def me():
    token = request.cookies.get("access_token")
    if not token:
        return jsonify({"error": "Unauthorized"}), 401

    decoded, role = decode_jwt(token)
    if not decoded:
        return jsonify({"error": "Invalid token"}), 401

    return jsonify({
        "id": decoded["sub"],
        "email": decoded.get("email"),
        "role": role,
        "app_metadata": decoded.get("app_metadata", {})
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    resp = make_response(jsonify({"ok": True}))
    resp.set_cookie("access_token", "", expires=0)
    return resp

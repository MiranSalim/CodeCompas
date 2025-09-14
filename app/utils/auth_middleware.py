from functools import wraps
from flask import request, jsonify
import requests
import os

from app.models import Profile

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
COOKIE_NAME = os.getenv("COOKIE_NAME", "session")


def require_auth(fn):
    """
    Decorator die auth-cookie uitleest en valideert via Supabase.
    Injecteert `user` object in de route functie.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.cookies.get(COOKIE_NAME)
        if not token:
            return jsonify({"error": "Not authenticated"}), 401

        # 1. Verifieer JWT via Supabase
        resp = requests.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {token}",
            },
        )

        if resp.status_code != 200:
            return jsonify({"error": "Invalid or expired token"}), 401

        user_data = resp.json()
        email = user_data.get("email")
        if not email:
            return jsonify({"error": "Invalid user"}), 401

        # 2. Zoek profiel in onze eigen database
        try:
            profile = Profile.get(Profile.email == email)
        except Profile.DoesNotExist:
            return jsonify({"error": "Profile not found"}), 403

        # 3. Geef user door aan de originele functie
        return fn(profile, *args, **kwargs)

    return wrapper

def require_admin(fn):
    """
    Decorator die eerst require_auth uitvoert,
    en daarna checkt of de gebruiker ADMIN is.
    """
    @require_auth
    @wraps(fn)
    def wrapper(user, *args, **kwargs):
        if getattr(user, "role", "USER") != "ADMIN":
            return jsonify({"error": "Forbidden, admin only"}), 403
        return fn(user, *args, **kwargs)

    return wrapper
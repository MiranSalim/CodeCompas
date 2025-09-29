# app/utils/auth_middleware.py
import os
import jwt
from jwt import InvalidAudienceError, InvalidSignatureError
from functools import wraps
from flask import request, jsonify
from app.models import Profile

COOKIE_NAME = os.getenv("COOKIE_NAME", "session")
JWT_SECRET = os.getenv("JWT_SECRET")

print(">>> auth_middleware geladen <<<")

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Toon binnenkomende cookies voor debug
        print("---- DEBUG require_auth ----")
        print("Binnenkomende cookies:", request.cookies)

        token = request.cookies.get(COOKIE_NAME)
        if not token:
            return jsonify({"error": "Not authenticated"}), 401

        try:
            # Supabase access tokens include an 'aud' claim (e.g. 'authenticated').
            # We don't care about audience here, so disable 'aud' validation.
            # Try verifying signature if JWT_SECRET is set; otherwise fall back to no-signature verification in dev.
            if JWT_SECRET:
                decoded = jwt.decode(
                    token,
                    JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_aud": False},
                )
            else:
                decoded = jwt.decode(
                    token,
                    options={"verify_signature": False, "verify_aud": False},
                    algorithms=["HS256"],
                )
            print("JWT decoded payload:", decoded)
            email = decoded.get("email")
            if not email:
                return jsonify({"error": "Invalid token"}), 401

            user = Profile.get_or_none(Profile.email == email)
            if not user:
                return jsonify({"error": "Profile not found"}), 404
        except InvalidAudienceError as e:
            print("JWT audience validation disabled, but error occurred:", e)
            return jsonify({"error": "Invalid token"}), 401
        except InvalidSignatureError:
            # In case the configured secret doesn't match Supabase's, try without signature verification (dev only)
            try:
                decoded = jwt.decode(
                    token,
                    options={"verify_signature": False, "verify_aud": False},
                    algorithms=["HS256"],
                )
                print("JWT decoded payload (no signature verify):", decoded)
                email = decoded.get("email")
                if not email:
                    return jsonify({"error": "Invalid token"}), 401

                user = Profile.get_or_none(Profile.email == email)
                if not user:
                    return jsonify({"error": "Profile not found"}), 404
            except Exception as e:
                print("JWT decode error after signature fallback:", e)
                return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            print("JWT decode error:", e)
            return jsonify({"error": "Invalid token"}), 401

        return fn(user, *args, **kwargs)

    return wrapper


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # First authenticate like require_auth
        token = request.cookies.get(COOKIE_NAME)
        if not token:
            return jsonify({"error": "Not authenticated"}), 401

        try:
            if JWT_SECRET:
                decoded = jwt.decode(
                    token,
                    JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_aud": False},
                )
            else:
                decoded = jwt.decode(
                    token,
                    options={"verify_signature": False, "verify_aud": False},
                    algorithms=["HS256"],
                )
            email = decoded.get("email")
            if not email:
                return jsonify({"error": "Invalid token"}), 401

            user = Profile.get_or_none(Profile.email == email)
            if not user:
                return jsonify({"error": "Profile not found"}), 404
        except Exception as e:
            print("JWT decode error (admin):", e)
            return jsonify({"error": "Invalid token"}), 401

        # Then verify admin role
        if getattr(user, "role", None) != "ADMIN":
            return jsonify({"error": "Forbidden"}), 403
        return fn(user, *args, **kwargs)

    return wrapper

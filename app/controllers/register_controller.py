from flask import Blueprint, request, jsonify
from supabase import create_client
import os
from app.models import Profile

register_bp = Blueprint("register", __name__)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)


@register_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    email = data.get("email")
    display_name = data.get("display_name")
    role = data.get("role")

    if not email or not role:
        return jsonify({"error": "Email and role required"}), 400

    try:
        # 🔑 Supabase user aanmaken
        user = supabase.auth.admin.create_user(
            {
                "email": email,
                "password": "lol",  # wordt via magic link gereset
                "email_confirm": True,
                "user_metadata": {"display_name": display_name},
                "app_metadata": {"role": role},
            }
        )

        user_id = user.user.id  # UUID van Supabase user

        # 🗄️ Profiel in database
        Profile.create(id=user_id, email=email, name=display_name, role=role)

        return jsonify({"ok": True, "id": str(user_id)}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

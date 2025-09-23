import os
import jwt
from flask import Blueprint, request, jsonify

debug_bp = Blueprint("debug", __name__)

@debug_bp.route("/debug/jwt", methods=["GET"])
def debug_jwt():
    token = request.cookies.get("access_token")
    if not token:
        return jsonify({"error": "No JWT cookie found"}), 401

    try:
        # alleen decoderen, zonder signature check
        decoded = jwt.decode(token, options={"verify_signature": False})
        return jsonify({"decoded": decoded})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

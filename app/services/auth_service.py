import os
import requests
from typing import Optional, Tuple

from ..models import Profile

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def login_and_get_token(email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (access_token, error_message). On success, error_message is None.
    """
    if not email or not password:
        return None, "Email and password required"

    resp = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers={
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
        },
        json={"email": email, "password": password},
    )

    if resp.status_code != 200:
        return None, "Invalid credentials"

    tokens = resp.json()
    access_token = tokens.get("access_token")
    if not access_token:
        return None, "Auth failed"

    # Ensure profile exists and is admin
    try:
        profile = Profile.get(Profile.email == email)
    except Profile.DoesNotExist:
        return None, "No profile found"

    if getattr(profile, "role", "USER") != "ADMIN":
        return None, "Forbidden"

    return access_token, None

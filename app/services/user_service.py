# app/services/user_service.py
import os
from typing import Tuple, Optional
from supabase import create_client
import logging

from ..models import Profile
from peewee import IntegrityError, fn

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DEFAULT_PASSWORD = "lol"


def create_user(email: str, display_name: Optional[str], role: str) -> Tuple[Optional[Profile], Optional[str]]:
    """
    Returns (profile, error_message). On success, error_message is None.
    """
    if not email:
        return None, "Email is required"

    if role not in ("TRAINEE", "ADMIN"):
        return None, "Invalid role"

    try:
        # Supabase create_user
        resp = supabase.auth.admin.create_user({
            "email": email,
            "password": DEFAULT_PASSWORD,
            "email_confirm": True,
            "user_metadata": {"name": display_name},
            "app_metadata": {"role": role},
        })
        logging.debug(f"Supabase admin.create_user response: {resp}")
        # Extract Supabase auth user id (UUID)
        supabase_user_id = None
        try:
            supabase_user_id = getattr(resp, "user", None)
            supabase_user_id = getattr(supabase_user_id, "id", None)
        except Exception:
            pass
        if not supabase_user_id:
            try:
                supabase_user_id = resp["user"]["id"]
            except Exception:
                pass
        if not supabase_user_id:
            return None, "Supabase create_user returned no user id"
    except Exception as e:
        logging.exception("Supabase create_user failed")
        return None, f"Supabase create_user failed: {str(e)}"

    # Zorg dat er een lokaal Profile bestaat
    try:
        profile, created = Profile.get_or_create(
            email=email,
            defaults={
                "id": supabase_user_id,
                "name": display_name,
                "role": role,
            }
        )
        if not created and getattr(profile, "id", None) is None:
            # If an old row lacks id, update it to the Supabase id
            profile.id = supabase_user_id
            profile.save()
    except Exception as e:
        logging.exception("Local Profile creation failed")
        return None, f"Local profile creation failed: {str(e)}"

    if not created:
        # Update bestaande waarden indien nodig
        updated = False
        if display_name and profile.name != display_name:
            profile.name = display_name
            updated = True
        if role and profile.role != role:
            profile.role = role
            updated = True
        if updated:
            profile.save()

    return profile, None

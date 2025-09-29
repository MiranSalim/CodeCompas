import os
from dotenv import load_dotenv
load_dotenv()  # laad .env automatisch


def _str_to_bool(s: str) -> bool:
    return str(s).lower() in ("1", "true", "yes")


class Config:
    # JWT / cookie
    JWT_SECRET = os.getenv("JWT_SECRET", "supergeheim")
    COOKIE_NAME = os.getenv("COOKIE_NAME", "session")
    COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "localhost")
    COOKIE_SECURE = _str_to_bool(os.getenv("COOKIE_SECURE", "False"))
    COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "None")  # None|Lax|Strict

    # CORS - comma separated in .env
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
    ).split(",")

    # Supabase (wordt uit .env gelezen)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # Postgres / Peewee
    PGHOST = os.getenv("PGHOST")
    PGPORT = int(os.getenv("PGPORT", 6543))
    PGDATABASE = os.getenv("PGDATABASE")
    PGUSER = os.getenv("PGUSER")
    PGPASSWORD = os.getenv("PGPASSWORD")

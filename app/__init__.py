from flask import Flask
from flask_cors import CORS

from .config import Config
from .models import create_tables, ensure_profile_id_autoincrement
from .db import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    origins = app.config.get("CORS_ORIGINS", ["http://localhost:5000"])
    CORS(app,
         resources={r"/api/*": {"origins": origins}},
         supports_credentials=True,
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization"],
    )

    from .routes.login_controller import login_bp
    from .routes.register_controller import register_bp
    from .routes.users_controller import users_bp
    app.register_blueprint(login_bp, url_prefix="/api")
    app.register_blueprint(register_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api")

    @app.before_request
    def _db_connect():
        if db.is_closed():
            db.connect()

    @app.teardown_request
    def _db_close(exc):
        if not db.is_closed():
            db.close()

    # ✅ maak tabellen bij startup
    with app.app_context():
        create_tables()
        ensure_profile_id_autoincrement()

    @app.route("/api/ping")
    def ping():
        return {"ok": True}

    return app

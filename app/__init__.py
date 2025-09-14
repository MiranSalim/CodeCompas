from flask_cors.extension import CORS
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from .config import Config
from .models import create_tables
from .db import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    origins = app.config.get("CORS_ORIGINS", ["http://localhost:5000"])
    CORS(app,
         resources={r"/api/*": {"origins": origins}},
         supports_credentials=True)

    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api")

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

    @app.route("/api/ping")
    def ping():
        return {"ok": True}

    return app

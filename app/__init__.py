from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from .config import Config
from .models import create_tables
from .db import db
from .controllers.login_controller import auth_bp
from .controllers.register_controller import register_bp
from .controllers.debug_controller import debug_bp


load_dotenv()  # zorg dat .env geladen is

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ CORS configuratie
    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173"]}},
        supports_credentials=True
    )

    # ✅ Database connectie hooks
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

    # ✅ Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(register_bp, url_prefix="/api")
    app.register_blueprint(debug_bp, url_prefix="/api")

    return app

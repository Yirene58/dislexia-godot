from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate, jwt
from app.routes.auth_routes import auth_bp
from app.models.user import User


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5173"]
            }
        }
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "message": "API Dislexia Godot funcionando"
        }), 200

    return app

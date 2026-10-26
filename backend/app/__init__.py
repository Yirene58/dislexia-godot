from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.extensions import db, migrate, jwt
from app.routes.auth_routes import auth_bp
from app.routes.character_routes import character_bp


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

    from app import models

    app.register_blueprint(auth_bp)
    app.register_blueprint(character_bp)

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "message": "Dislexia Godot API funcionando"
        }), 200

    from app.routes.save_routes import save_bp
    app.register_blueprint(save_bp)
    from app.routes.game_routes import game_bp
    app.register_blueprint(game_bp)

    from app.routes.ia_routes import ia_bp
    app.register_blueprint(ia_bp)

    from app.routes.progreso_routes import progreso_bp
    app.register_blueprint(progreso_bp)

    return app


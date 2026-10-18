from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.character import Character
from app.models.save_game import SaveGame

game_bp = Blueprint("game", __name__)


@game_bp.route(
    "/api/game/characters/<int:character_id>/bootstrap",
    methods=["GET"],
)
@jwt_required()
def bootstrap_game(character_id):
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({
            "message": "Identidad de usuario no valida"
        }), 401

    character = db.session.query(Character).filter_by(
        id=character_id,
        user_id=user_id,
    ).first()

    if character is None:
        return jsonify({
            "message": "Personaje no encontrado"
        }), 404

    save = db.session.query(SaveGame).filter_by(
        character_id=character.id
    ).first()

    return jsonify({
        "status": 200,
        "message": "Datos del juego consultados correctamente",
        "data": {
            "character": {
                "id": character.id,
                "name": character.name,
                "character_class": character.character_class,
                "level": character.level,
                "experience": character.experience,
            },
            "save": save.to_dict() if save else None,
            "has_save": save is not None,
        }
    }), 200

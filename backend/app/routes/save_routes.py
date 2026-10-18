from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.character import Character
from app.models.save_game import SaveGame

save_bp = Blueprint("save_games", __name__)


def get_owned_character(character_id):
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None

    return db.session.query(Character).filter_by(
        id=character_id,
        user_id=user_id,
    ).first()


@save_bp.route(
    "/api/characters/<int:character_id>/save",
    methods=["GET"],
)
@jwt_required()
def get_save(character_id):
    character = get_owned_character(character_id)

    if character is None:
        return jsonify({
            "message": "Personaje no encontrado",
        }), 404

    save = db.session.query(SaveGame).filter_by(
        character_id=character.id
    ).first()

    return jsonify({
        "status": 200,
        "message": "Consulta realizada correctamente",
        "data": save.to_dict() if save else None,
    }), 200


@save_bp.route(
    "/api/characters/<int:character_id>/save",
    methods=["PUT"],
)
@jwt_required()
def update_save(character_id):
    character = get_owned_character(character_id)

    if character is None:
        return jsonify({
            "message": "Personaje no encontrado",
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "message": "Se requiere un objeto JSON",
        }), 400

    world_id = data.get("world_id")
    checkpoint_id = data.get("checkpoint_id")
    status = data.get("status", "in_progress")
    progress_data = data.get("progress_data", {})

    if not isinstance(world_id, str) or not 1 <= len(world_id) <= 100:
        return jsonify({
            "message": "world_id debe tener entre 1 y 100 caracteres",
        }), 400

    if not isinstance(checkpoint_id, str) or len(checkpoint_id) > 100:
        return jsonify({
            "message": "checkpoint_id no es valido",
        }), 400

    if status not in ("in_progress", "completed"):
        return jsonify({
            "message": "Estado de partida no valido",
        }), 400

    if not isinstance(progress_data, dict):
        return jsonify({
            "message": "progress_data debe ser un objeto JSON",
        }), 400

    save = db.session.query(SaveGame).filter_by(
        character_id=character.id
    ).first()

    if save is None:
        save = SaveGame(character_id=character.id)
        db.session.add(save)

    save.world_id = world_id
    save.checkpoint_id = checkpoint_id
    save.status = status
    save.progress_data = progress_data

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "message": "No se pudo guardar la partida",
        }), 500

    return jsonify({
        "status": 200,
        "message": "Partida guardada correctamente",
        "data": save.to_dict(),
    }), 200


@save_bp.route(
    "/api/characters/<int:character_id>/save",
    methods=["DELETE"],
)
@jwt_required()
def delete_save(character_id):
    character = get_owned_character(character_id)

    if character is None:
        return jsonify({
            "message": "Personaje no encontrado",
        }), 404

    save = db.session.query(SaveGame).filter_by(
        character_id=character.id
    ).first()

    if save is None:
        return jsonify({
            "message": "No existe una partida guardada",
        }), 404

    try:
        db.session.delete(save)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({
            "message": "No se pudo eliminar la partida",
        }), 500

    return jsonify({
        "status": 200,
        "message": "Partida eliminada correctamente",
    }), 200

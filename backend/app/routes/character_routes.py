from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.character import Character


character_bp = Blueprint(
    "characters",
    __name__,
    url_prefix="/api/characters"
)

VALID_CLASSES = {
    "warrior",
    "mage",
    "archer"
}


def serialize_character(character):
    return {
        "id": character.id,
        "name": character.name,
        "character_class": character.character_class,
        "level": character.level,
        "experience": character.experience
    }


@character_bp.get("")
@jwt_required()
def get_characters():
    user_id = int(get_jwt_identity())

    characters = Character.query.filter_by(
        user_id=user_id
    ).all()

    return jsonify({
        "status": 200,
        "message": "Personajes consultados correctamente",
        "data": [
            serialize_character(character)
            for character in characters
        ]
    }), 200


@character_bp.post("")
@jwt_required()
def create_character():
    user_id = int(get_jwt_identity())

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    character_class = str(
        data.get("character_class", "")
    ).strip().lower()

    if not 3 <= len(name) <= 50:
        return jsonify({
            "message": "El nombre debe tener entre 3 y 50 caracteres"
        }), 400

    if character_class not in VALID_CLASSES:
        return jsonify({
            "message": "Clase de personaje no válida"
        }), 400

    character = Character(
        user_id=user_id,
        name=name,
        character_class=character_class,
        level=1,
        experience=0
    )

    db.session.add(character)
    db.session.commit()

    return jsonify({
        "status": 201,
        "message": "Personaje creado correctamente",
        "data": serialize_character(character)
    }), 201


@character_bp.get("/<int:character_id>")
@jwt_required()
def get_character(character_id):
    user_id = int(get_jwt_identity())

    character = Character.query.filter_by(
        id=character_id,
        user_id=user_id
    ).first()

    if not character:
        return jsonify({
            "message": "Personaje no encontrado"
        }), 404

    return jsonify({
        "data": serialize_character(character)
    }), 200


@character_bp.delete("/<int:character_id>")
@jwt_required()
def delete_character(character_id):
    user_id = int(get_jwt_identity())

    character = Character.query.filter_by(
        id=character_id,
        user_id=user_id
    ).first()

    if not character:
        return jsonify({
            "message": "Personaje no encontrado"
        }), 404

    db.session.delete(character)
    db.session.commit()

    return jsonify({
        "message": "Personaje eliminado correctamente"
    }), 200
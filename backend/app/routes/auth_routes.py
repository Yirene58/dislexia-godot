from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from sqlalchemy import or_

from app.extensions import db
from app.models.user import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    if (
        not username
        or "@" not in email
        or not isinstance(password, str)
        or len(password) < 8
    ):
        return jsonify({
            "message": "Datos de registro invalidos"
        }), 400

    existing = User.query.filter(
        or_(
            User.username == username,
            User.email == email
        )
    ).first()

    if existing:
        return jsonify({
            "message": "El usuario o correo ya existe"
        }), 409

    user = User(
        username=username,
        email=email
    )

    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Usuario registrado correctamente",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    identifier = str(data.get("identifier", "")).strip()
    password = data.get("password", "")

    user = User.query.filter(
        or_(
            User.username == identifier,
            User.email == identifier.lower()
        )
    ).first()

    if (
        not user
        or not isinstance(password, str)
        or not user.check_password(password)
    ):
        return jsonify({
            "message": "Credenciales incorrectas"
        }), 401

    token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "message": "Inicio de sesion exitoso",
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = db.session.get(User, int(user_id))

    if not user:
        return jsonify({
            "message": "Usuario no encontrado"
        }), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email
    }), 200

"""Ruta de voz: GET /api/voz?texto=pe&velocidad=lenta  -> audio WAV (RF5)."""
from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import jwt_required

from app.services import voz

voz_bp = Blueprint("voz", __name__, url_prefix="/api/voz")


@voz_bp.route("", methods=["GET"])
@jwt_required()
def hablar():
    if not voz.disponible():
        return jsonify({"message": "La voz no está instalada en el servidor"}), 503
    texto = request.args.get("texto", "")
    velocidad = request.args.get("velocidad", "normal")
    try:
        datos = voz.audio_wav(texto, velocidad)
    except ValueError:
        return jsonify({"message": "Texto no válido"}), 400
    except Exception:
        return jsonify({"message": "No se pudo generar el audio"}), 500
    return Response(datos, mimetype="audio/wav",
                    headers={"Cache-Control": "private, max-age=86400"})


@voz_bp.route("/estado", methods=["GET"])
def estado():
    return jsonify({"voz": "ok" if voz.disponible() else "no instalada",
                    "modelo": voz.MODELO}), 200

"""Rutas de progreso del niño: intentos (tabla Intento), dificultad adaptativa,
niveles de un mundo, logros y estado del jugador.

Historias: RF3, RF4, RF6, RF12, RF13, RF16, RF18, RF38, RF39, RF43.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models.character import Character
from app.models.progreso import (
    CambioDificultad, DificultadMundo, EstadoJugador, Intento, Logro,
)
from app.services.adaptacion import EstadoAdaptativo, aplicar_resultado, nivel_recomendado

progreso_bp = Blueprint("progreso", __name__, url_prefix="/api/characters")

# Mundos del mapa (RF2) y cuántos niveles tiene cada uno (RF13).
MUNDOS = {
    "mundo_1": {"nombre": "Mundo 1", "niveles": 3},
    "mundo_2": {"nombre": "Mundo 2", "niveles": 3},
    "mundo_3": {"nombre": "Mundo 3", "niveles": 3},
    "mundo_4": {"nombre": "Mundo 4", "niveles": 3},
    "mundo_5": {"nombre": "Mundo 5", "niveles": 3},
}
NOMBRES_NIVEL = {1: "Palabras de 2 sílabas", 2: "Palabras de 3 sílabas", 3: "Sílabas difíciles"}
TIPOS_ERROR = {"inversion", "sustitucion", "orden", "omision", "separacion"}


# ------------------------------------------------------------------ utilidades

def _personaje_propio(character_id):
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None
    return db.session.query(Character).filter_by(id=character_id, user_id=user_id).first()


def _no_encontrado():
    return jsonify({"message": "Personaje no encontrado"}), 404


def _mundo_valido(world_id):
    return world_id in MUNDOS


def _dificultad(character_id, world_id):
    fila = db.session.query(DificultadMundo).filter_by(
        character_id=character_id, world_id=world_id).first()
    if fila is None:
        fila = DificultadMundo(character_id=character_id, world_id=world_id,
                               dificultad=1, racha_aciertos=0, racha_fallos=0)
        db.session.add(fila)
    return fila


def dificultad_actual(character_id, world_id):
    """La usan otras rutas (por ejemplo la IA de sílabas) para respetar RF4/RF13."""
    fila = db.session.query(DificultadMundo).filter_by(
        character_id=character_id, world_id=world_id).first()
    return fila.dificultad if fila else 1


def _codigos_obtenidos(character_id):
    return {l.codigo for l in db.session.query(Logro).filter_by(character_id=character_id)}


def _codigo_nivel(world_id, nivel):
    return f"{world_id}:nivel_{nivel}"


def _codigo_mundo(world_id):
    return f"{world_id}:completado"


def _estado_jugador(character_id):
    fila = db.session.query(EstadoJugador).filter_by(character_id=character_id).first()
    if fila is None:
        fila = EstadoJugador(character_id=character_id, mundo_actual="mundo_1")
        db.session.add(fila)
    return fila


def _niveles(character_id, world_id):
    total = MUNDOS[world_id]["niveles"]
    obtenidos = _codigos_obtenidos(character_id)
    estadisticas = dict(
        ((nivel, (intentos, errores)) for nivel, intentos, errores in db.session.query(
            Intento.nivel,
            func.count(Intento.id),
            func.sum(db.case((Intento.correcto.is_(False), 1), else_=0)),
        ).filter(
            Intento.character_id == character_id,
            Intento.world_id == world_id,
            Intento.por_inactividad.is_(False),
        ).group_by(Intento.nivel))
    )
    niveles = []
    for n in range(1, total + 1):
        completado = _codigo_nivel(world_id, n) in obtenidos
        anterior_ok = n == 1 or _codigo_nivel(world_id, n - 1) in obtenidos
        intentos, errores = estadisticas.get(n, (0, 0))
        niveles.append({
            "nivel": n,
            "nombre": NOMBRES_NIVEL.get(n, f"Nivel {n}"),
            "desbloqueado": anterior_ok or completado,
            "completado": completado,
            "intentos": int(intentos or 0),
            "errores": int(errores or 0),
        })
    recomendado = nivel_recomendado(niveles)
    for n in niveles:
        n["recomendado"] = n["nivel"] == recomendado
    return niveles


# ------------------------------------------------------------------ rutas

@progreso_bp.route("/<int:character_id>/intentos", methods=["POST"])
@jwt_required()
def registrar_intento(character_id):
    """Registra una respuesta del niño y aplica el módulo adaptativo (RF4).

    Cuerpo: {"world_id": "mundo_1", "nivel": 1, "ejercicio": "pelota",
             "respuesta": ["pe", "ta"], "correcto": false, "tipo_error": "orden",
             "tiempo_ms": 3200, "es_repeticion": false, "por_inactividad": false,
             "completo": true}
    """
    personaje = _personaje_propio(character_id)
    if personaje is None:
        return _no_encontrado()
    d = request.get_json(silent=True)
    if not isinstance(d, dict):
        return jsonify({"message": "Se requiere un objeto JSON"}), 400

    world_id = d.get("world_id")
    ejercicio = d.get("ejercicio")
    correcto = d.get("correcto")
    if not isinstance(world_id, str) or not _mundo_valido(world_id):
        return jsonify({"message": "world_id no es valido"}), 400
    if not isinstance(ejercicio, str) or not 1 <= len(ejercicio) <= 100:
        return jsonify({"message": "ejercicio debe tener entre 1 y 100 caracteres"}), 400
    if not isinstance(correcto, bool):
        return jsonify({"message": "correcto debe ser true o false"}), 400
    try:
        nivel = int(d.get("nivel", 1))
        tiempo_ms = int(d["tiempo_ms"]) if d.get("tiempo_ms") is not None else None
    except (TypeError, ValueError):
        return jsonify({"message": "nivel y tiempo_ms deben ser numeros"}), 400
    if not 1 <= nivel <= MUNDOS[world_id]["niveles"]:
        return jsonify({"message": "nivel no es valido"}), 400
    tipo_error = d.get("tipo_error")
    if tipo_error is not None and tipo_error not in TIPOS_ERROR:
        tipo_error = None
    respuesta = d.get("respuesta")
    if respuesta is not None and not (isinstance(respuesta, list) and len(respuesta) <= 20):
        respuesta = None
    por_inactividad = bool(d.get("por_inactividad", False))
    completo = bool(d.get("completo", True))

    fila = _dificultad(character_id, world_id)
    intento = Intento(
        character_id=character_id, world_id=world_id, nivel=nivel,
        ejercicio=ejercicio.strip().lower(), respuesta=respuesta,
        correcto=correcto, tipo_error=None if correcto else tipo_error,
        tiempo_ms=tiempo_ms, dificultad=fila.dificultad,
        es_repeticion=bool(d.get("es_repeticion", False)),
        por_inactividad=por_inactividad, completo=completo,
    )
    db.session.add(intento)

    cambio = None
    # RF39 / RF18: la inactividad y los abandonos se registran, pero no son errores del niño
    if not por_inactividad and completo:
        estado = EstadoAdaptativo(fila.dificultad, fila.racha_aciertos, fila.racha_fallos)
        anterior = fila.dificultad
        estado, cambio, motivo = aplicar_resultado(estado, correcto)
        fila.dificultad = estado.dificultad
        fila.racha_aciertos = estado.racha_aciertos
        fila.racha_fallos = estado.racha_fallos
        if cambio:
            db.session.add(CambioDificultad(character_id=character_id, world_id=world_id,
                                            anterior=anterior, nueva=fila.dificultad,
                                            motivo=motivo))
    _estado_jugador(character_id).mundo_actual = world_id

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "No se pudo guardar el intento"}), 500

    return jsonify({
        "message": "Intento registrado",
        "data": {"intento_id": intento.id, "dificultad": fila.dificultad, "cambio": cambio,
                 "racha_aciertos": fila.racha_aciertos, "racha_fallos": fila.racha_fallos},
    }), 201


@progreso_bp.route("/<int:character_id>/mundos/<world_id>", methods=["GET"])
@jwt_required()
def estado_mundo(character_id, world_id):
    """Pantalla de niveles (RF13): niveles bloqueados, completados y recomendado."""
    if _personaje_propio(character_id) is None:
        return _no_encontrado()
    if not _mundo_valido(world_id):
        return jsonify({"message": "Mundo no encontrado"}), 404
    niveles = _niveles(character_id, world_id)
    return jsonify({
        "message": "Estado del mundo",
        "data": {
            "world_id": world_id,
            "nombre": MUNDOS[world_id]["nombre"],
            "dificultad": dificultad_actual(character_id, world_id),
            "niveles": niveles,
            "completado": all(n["completado"] for n in niveles),
        },
    }), 200


@progreso_bp.route("/<int:character_id>/mundos/<world_id>/niveles/<int:nivel>/completar",
                   methods=["POST"])
@jwt_required()
def completar_nivel(character_id, world_id, nivel):
    """Marca un nivel como completado y entrega insignias (RF6, RF38)."""
    if _personaje_propio(character_id) is None:
        return _no_encontrado()
    if not _mundo_valido(world_id) or not 1 <= nivel <= MUNDOS[world_id]["niveles"]:
        return jsonify({"message": "Nivel no encontrado"}), 404
    niveles = _niveles(character_id, world_id)
    if not niveles[nivel - 1]["desbloqueado"]:
        return jsonify({"message": "Ese nivel todavia esta bloqueado"}), 409

    obtenidos = _codigos_obtenidos(character_id)
    nuevos = []
    codigo = _codigo_nivel(world_id, nivel)
    if codigo not in obtenidos:
        db.session.add(Logro(character_id=character_id, world_id=world_id, codigo=codigo))
        obtenidos.add(codigo)
        nuevos.append(codigo)
    total = MUNDOS[world_id]["niveles"]
    mundo_completado = all(_codigo_nivel(world_id, n) in obtenidos for n in range(1, total + 1))
    if mundo_completado and _codigo_mundo(world_id) not in obtenidos:
        db.session.add(Logro(character_id=character_id, world_id=world_id,
                             codigo=_codigo_mundo(world_id)))
        nuevos.append(_codigo_mundo(world_id))
    estado = _estado_jugador(character_id)
    estado.mundo_actual = world_id
    estado.ejercicio_pendiente = None
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "No se pudo guardar el progreso"}), 500
    return jsonify({
        "message": "Nivel completado",
        "data": {"nuevos_logros": nuevos, "mundo_completado": mundo_completado,
                 "niveles": _niveles(character_id, world_id)},
    }), 200


@progreso_bp.route("/<int:character_id>/logros", methods=["GET"])
@jwt_required()
def logros(character_id):
    """"Mis logros" (RF6): obtenidos y pendientes (en silueta), agrupados por mundo."""
    if _personaje_propio(character_id) is None:
        return _no_encontrado()
    fechas = {l.codigo: l.obtenido_en.isoformat()
              for l in db.session.query(Logro).filter_by(character_id=character_id)}
    resultado = []
    for world_id, info in MUNDOS.items():
        insignias = []
        for n in range(1, info["niveles"] + 1):
            c = _codigo_nivel(world_id, n)
            insignias.append({"codigo": c, "nombre": f"Nivel {n}",
                              "obtenido": c in fechas, "fecha": fechas.get(c)})
        c = _codigo_mundo(world_id)
        insignias.append({"codigo": c, "nombre": f"{info['nombre']} completado",
                          "obtenido": c in fechas, "fecha": fechas.get(c), "especial": True})
        resultado.append({"world_id": world_id, "nombre": info["nombre"], "insignias": insignias})
    return jsonify({"message": "Logros", "data": resultado}), 200


@progreso_bp.route("/<int:character_id>/estado-juego", methods=["GET", "PUT"])
@jwt_required()
def estado_juego(character_id):
    """Dónde quedó el niño y si dejó un ejercicio a medias (RF16, RF18, RF43)."""
    if _personaje_propio(character_id) is None:
        return _no_encontrado()
    estado = _estado_jugador(character_id)
    if request.method == "PUT":
        d = request.get_json(silent=True) or {}
        mundo = d.get("mundo_actual")
        if mundo is not None:
            if not _mundo_valido(mundo):
                return jsonify({"message": "mundo_actual no es valido"}), 400
            estado.mundo_actual = mundo
        if "ejercicio_pendiente" in d:
            pendiente = d["ejercicio_pendiente"]
            if pendiente is not None and not isinstance(pendiente, dict):
                return jsonify({"message": "ejercicio_pendiente debe ser un objeto o null"}), 400
            estado.ejercicio_pendiente = pendiente
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "No se pudo guardar el estado"}), 500
    return jsonify({"message": "Estado del jugador", "data": estado.to_dict()}), 200

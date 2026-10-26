"""Capa de datos del progreso del niño (RF4, RF6, RF12, RF16, RF18, RF39, RF43).

- Intento: cada respuesta del niño (la tabla "Intento" de las historias de usuario).
- DificultadMundo: dificultad actual por personaje y mundo (RF4), con sus rachas.
- CambioDificultad: historial de cambios de dificultad (trazabilidad RF4/RF40).
- Logro: insignias obtenidas (RF6, RF38).
- EstadoJugador: dónde quedó el niño y si dejó un ejercicio a medias (RF16, RF18, RF43).
"""
from datetime import datetime, timezone

from app.extensions import db


def _ahora():
    return datetime.now(timezone.utc)


def _iso(fecha):
    return fecha.isoformat() if fecha else None


class Intento(db.Model):
    __tablename__ = "intentos"

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=False, index=True)
    world_id = db.Column(db.String(50), nullable=False, index=True)
    nivel = db.Column(db.Integer, nullable=False, default=1)
    ejercicio = db.Column(db.String(100), nullable=False)      # ej. la palabra "pelota"
    respuesta = db.Column(db.JSON, nullable=True)               # lo que eligió el niño
    correcto = db.Column(db.Boolean, nullable=False, default=False)
    tipo_error = db.Column(db.String(30), nullable=True)        # inversion, sustitucion, orden...
    tiempo_ms = db.Column(db.Integer, nullable=True)            # tiempo de respuesta
    dificultad = db.Column(db.Integer, nullable=False, default=1)
    es_repeticion = db.Column(db.Boolean, nullable=False, default=False)   # RF12
    por_inactividad = db.Column(db.Boolean, nullable=False, default=False)  # RF39 (no es error)
    completo = db.Column(db.Boolean, nullable=False, default=True)          # RF18 (False = abandonado)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_ahora)

    character = db.relationship(
        "Character", backref=db.backref("intentos", cascade="all, delete-orphan"))

    def to_dict(self):
        return {
            "id": self.id, "world_id": self.world_id, "nivel": self.nivel,
            "ejercicio": self.ejercicio, "respuesta": self.respuesta,
            "correcto": self.correcto, "tipo_error": self.tipo_error,
            "tiempo_ms": self.tiempo_ms, "dificultad": self.dificultad,
            "es_repeticion": self.es_repeticion, "por_inactividad": self.por_inactividad,
            "completo": self.completo, "created_at": _iso(self.created_at),
        }


class DificultadMundo(db.Model):
    __tablename__ = "dificultad_mundo"
    __table_args__ = (db.UniqueConstraint("character_id", "world_id", name="uq_dificultad_personaje_mundo"),)

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=False, index=True)
    world_id = db.Column(db.String(50), nullable=False)
    dificultad = db.Column(db.Integer, nullable=False, default=1)
    racha_aciertos = db.Column(db.Integer, nullable=False, default=0)
    racha_fallos = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_ahora, onupdate=_ahora)

    character = db.relationship(
        "Character", backref=db.backref("dificultades", cascade="all, delete-orphan"))


class CambioDificultad(db.Model):
    __tablename__ = "cambios_dificultad"

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=False, index=True)
    world_id = db.Column(db.String(50), nullable=False)
    anterior = db.Column(db.Integer, nullable=False)
    nueva = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(60), nullable=False)   # "5 aciertos seguidos", "3 fallos seguidos"
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_ahora)

    character = db.relationship(
        "Character", backref=db.backref("cambios_dificultad", cascade="all, delete-orphan"))


class Logro(db.Model):
    __tablename__ = "logros"
    __table_args__ = (db.UniqueConstraint("character_id", "codigo", name="uq_logro_personaje_codigo"),)

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=False, index=True)
    world_id = db.Column(db.String(50), nullable=False)
    codigo = db.Column(db.String(80), nullable=False)    # "mundo_1:nivel_2", "mundo_1:completado"
    obtenido_en = db.Column(db.DateTime(timezone=True), nullable=False, default=_ahora)

    character = db.relationship(
        "Character", backref=db.backref("logros", cascade="all, delete-orphan"))


class EstadoJugador(db.Model):
    __tablename__ = "estado_jugador"

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=False, unique=True)
    mundo_actual = db.Column(db.String(50), nullable=False, default="mundo_1")
    ejercicio_pendiente = db.Column(db.JSON, nullable=True)   # RF43: ejercicio sin terminar
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=_ahora, onupdate=_ahora)

    character = db.relationship(
        "Character", backref=db.backref("estado_jugador", cascade="all, delete-orphan", uselist=False))

    def to_dict(self):
        return {"mundo_actual": self.mundo_actual,
                "ejercicio_pendiente": self.ejercicio_pendiente,
                "updated_at": _iso(self.updated_at)}

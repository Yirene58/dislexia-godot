"""Módulo de IA adaptativa (RF4) — capa lógica, independiente de la interfaz y de la base de datos.

Reglas del documento del proyecto:
  - 3 fallos consecutivos  -> baja la dificultad un nivel.
  - 5 aciertos consecutivos -> sube la dificultad un nivel (de a uno, sin saltos).
  - Los intentos por inactividad (RF39) o abandonados (RF18) se registran pero no cuentan.
Se puede reemplazar por otro algoritmo sin tocar Godot ni la base de datos.
"""
from dataclasses import dataclass

DIFICULTAD_MIN = 1
DIFICULTAD_MAX = 3
FALLOS_PARA_BAJAR = 3
ACIERTOS_PARA_SUBIR = 5


@dataclass
class EstadoAdaptativo:
    dificultad: int = DIFICULTAD_MIN
    racha_aciertos: int = 0
    racha_fallos: int = 0


def aplicar_resultado(estado: EstadoAdaptativo, correcto: bool):
    """Actualiza el estado con un intento. Devuelve (estado, cambio, motivo).

    cambio: "sube", "baja" o None.
    """
    cambio, motivo = None, None
    if correcto:
        estado.racha_aciertos += 1
        estado.racha_fallos = 0
        if estado.racha_aciertos >= ACIERTOS_PARA_SUBIR:
            estado.racha_aciertos = 0
            if estado.dificultad < DIFICULTAD_MAX:
                estado.dificultad += 1
                cambio, motivo = "sube", f"{ACIERTOS_PARA_SUBIR} aciertos seguidos"
    else:
        estado.racha_fallos += 1
        estado.racha_aciertos = 0
        if estado.racha_fallos >= FALLOS_PARA_BAJAR:
            estado.racha_fallos = 0
            if estado.dificultad > DIFICULTAD_MIN:
                estado.dificultad -= 1
                cambio, motivo = "baja", f"{FALLOS_PARA_BAJAR} fallos seguidos"
    return estado, cambio, motivo


def nivel_recomendado(niveles):
    """niveles: lista de dicts con nivel, desbloqueado, completado, errores, intentos.

    Recomienda el primer nivel desbloqueado sin completar; si todos están completos,
    el que tuvo más proporción de errores (para reforzar).
    """
    for n in niveles:
        if n["desbloqueado"] and not n["completado"]:
            return n["nivel"]
    completos = [n for n in niveles if n["intentos"] > 0]
    if not completos:
        return niveles[0]["nivel"] if niveles else None
    return max(completos, key=lambda n: n["errores"] / n["intentos"])["nivel"]

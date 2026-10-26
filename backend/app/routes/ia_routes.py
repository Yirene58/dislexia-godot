"""Rutas de IA: genera palabras para el minijuego de sílabas usando Ollama.

La IA solo PROPONE palabras. La separación en sílabas la hace silabas.py
(por reglas), así nunca se le enseña a un niño una división incorrecta.
Si Ollama no responde, se usa un banco fijo de palabras.
"""
import json
import os
import random
import urllib.request

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.services.silabas import (
    NOMBRES_DIFICULTAD, dificultades, opciones_con_distractores, silabear,
    tipo_de_error,
)

ia_bp = Blueprint("ia", __name__, url_prefix="/api/ia")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
TIEMPO_MAXIMO = int(os.environ.get("OLLAMA_TIMEOUT", "60"))

# dificultad -> (mínimo de sílabas, máximo de sílabas)
SILABAS_POR_DIFICULTAD = {1: (2, 2), 2: (3, 3), 3: (3, 4)}

BANCO = [
    "gato", "casa", "mesa", "luna", "sapo", "pato", "dedo", "foca", "vaca", "rosa",
    "pelota", "camisa", "conejo", "manzana", "tomate", "zapato", "paloma", "ventana",
    "mariposa", "elefante", "chocolate", "bicicleta", "dinosaurio", "tortuga", "cocodrilo",
]


def _palabras_validas(candidatas, dificultad, cantidad):
    minimo, maximo = SILABAS_POR_DIFICULTAD[dificultad]
    vistas, resultado = set(), []
    for palabra in candidatas:
        if not isinstance(palabra, str):
            continue
        palabra = palabra.strip().lower()
        if palabra in vistas or not palabra.isalpha() or len(palabra) > 14:
            continue
        silabas = silabear(palabra)
        if minimo <= len(silabas) <= maximo:
            vistas.add(palabra)
            resultado.append({"palabra": palabra, "silabas": silabas})
        if len(resultado) == cantidad:
            break
    return resultado


def _pedir_a_ollama(tema, dificultad, cantidad):
    minimo, maximo = SILABAS_POR_DIFICULTAD[dificultad]
    prompt = (
        "Eres un asistente para un juego educativo de lectura para niños de 6 a 8 años "
        "con dislexia. Escribe una lista de {n} palabras sencillas en español, "
        "sustantivos comunes y conocidos por niños, relacionados con el tema '{tema}', "
        "que tengan entre {mi} y {ma} sílabas. Sin nombres propios, sin palabras "
        "ofensivas ni de miedo. Responde SOLO con JSON con esta forma: "
        '{{"palabras": ["palabra1", "palabra2"]}}'
    ).format(n=cantidad * 3, tema=tema, mi=minimo, ma=maximo)

    cuerpo = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.8},
    }).encode("utf-8")
    peticion = urllib.request.Request(
        OLLAMA_URL + "/api/generate",
        data=cuerpo,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(peticion, timeout=TIEMPO_MAXIMO) as respuesta:
        datos = json.loads(respuesta.read().decode("utf-8"))
    contenido = json.loads(datos.get("response", "{}"))
    palabras = contenido.get("palabras", []) if isinstance(contenido, dict) else []
    return palabras if isinstance(palabras, list) else []


@ia_bp.route("/silabas", methods=["POST"])
@jwt_required()
def generar_silabas():
    datos = request.get_json(silent=True) or {}
    tema = str(datos.get("tema", "animales")).strip()[:40] or "animales"

    try:
        dificultad = int(datos.get("dificultad", 1))
        cantidad = int(datos.get("cantidad", 5))
    except (TypeError, ValueError):
        return jsonify({"message": "dificultad y cantidad deben ser números"}), 400

    dificultad = min(max(dificultad, 1), 3)
    cantidad = min(max(cantidad, 1), 10)

    palabras, fuente = [], "ia"
    try:
        palabras = _palabras_validas(
            _pedir_a_ollama(tema, dificultad, cantidad), dificultad, cantidad)
    except Exception:
        palabras = []

    if len(palabras) < cantidad:
        fuente = "banco" if not palabras else "ia+banco"
        ya = {p["palabra"] for p in palabras}
        extra = [p for p in BANCO if p not in ya]
        random.shuffle(extra)
        palabras += _palabras_validas(extra, dificultad, cantidad - len(palabras))

    for p in palabras:
        p["opciones"] = opciones_con_distractores(p["silabas"])

    return jsonify({
        "message": "Palabras generadas",
        "data": {"palabras": palabras, "fuente": fuente, "dificultad": dificultad},
    }), 200


@ia_bp.route("/estado", methods=["GET"])
def estado_ia():
    try:
        with urllib.request.urlopen(OLLAMA_URL + "/api/tags", timeout=3) as r:
            modelos = [m.get("name") for m in json.loads(r.read()).get("models", [])]
        return jsonify({"ollama": "ok", "modelo": OLLAMA_MODEL,
                        "modelo_instalado": OLLAMA_MODEL in modelos}), 200
    except Exception:
        return jsonify({"ollama": "apagado", "modelo": OLLAMA_MODEL}), 200


# ---------------------------------------------------------------------------
# Refuerzo adaptativo: según los errores, palabras parecidas pero más sencillas
# ---------------------------------------------------------------------------
BANCO_REFUERZO = {
    "grupo_consonantico": ["clavo", "blusa", "libro", "plato", "fresa", "globo",
                           "brazo", "trigo", "grillo", "cabra", "tigre", "crema"],
    "diptongo": ["agua", "nieve", "huevo", "rueda", "peine", "cielo",
                 "jaula", "auto", "reina", "suelo", "piano", "tierra"],
    "hiato": ["río", "día", "tía", "tío", "oído", "canoa",
              "boa", "poeta", "museo", "correo", "deseo", "paseo"],
    "silaba_trabada": ["barco", "carta", "torta", "papel", "mantel", "perla",
                       "pulpo", "circo", "campo", "lápiz", "martes", "sartén"],
    "silaba_inversa": ["isla", "alto", "alga", "ardilla", "asno", "orca",
                       "olmo", "urna", "alce", "arpa", "ancho", "orla"],
    "letras_espejo": ["dado", "pato", "bota", "dedo", "papá", "boca",
                      "pipa", "duda", "bebé", "dama", "pepa", "queso"],
    "palabra_larga": ["gato", "casa", "mesa", "luna", "sapo", "vaca",
                      "rosa", "foca", "pelota", "conejo", "camisa", "tomate"],
}


def _objetivo(analisis):
    """Elige la dificultad que más se repite en las palabras falladas."""
    conteo = {}
    for a in analisis:
        for t in a["dificultades"]:
            peso = 1
            # confundir b/d/p/q pesa más si el error fue cambiar letras
            if t == "letras_espejo":
                peso = 3 if a["tipo_error"] == "sustitucion" else 0
            conteo[t] = conteo.get(t, 0) + peso
        if a["tipo_error"] == "inversion":
            # confunde "la" con "al": practicar sílabas inversas
            conteo["silaba_inversa"] = conteo.get("silaba_inversa", 0) + 2
    conteo = {k: v for k, v in conteo.items() if v > 0}
    if not conteo:
        return None
    # palabra_larga solo si no hay otra dificultad más concreta
    concretas = {k: v for k, v in conteo.items() if k != "palabra_larga"}
    elegido = concretas or conteo
    return max(elegido, key=elegido.get)


def _es_mas_sencilla(palabra, objetivo, max_silabas, excluir):
    p = palabra.strip().lower()
    if not p.isalpha() or p in excluir or len(p) > 12:
        return None
    sil = silabear(p)
    if not 2 <= len(sil) <= max_silabas:
        return None
    difs = dificultades(p)
    if objetivo and objetivo != "palabra_larga" and objetivo not in difs:
        return None
    # más sencilla = no trae dificultades extra (aparte del objetivo)
    extra = difs - {objetivo, "letras_espejo"}
    if extra:
        return None
    return {"palabra": p, "silabas": sil}


def _ollama_refuerzo(falladas, objetivo, max_silabas, cantidad):
    descripcion = NOMBRES_DIFICULTAD.get(objetivo, "palabras cortas y sencillas")
    ejemplos = ", ".join(BANCO_REFUERZO.get(objetivo, BANCO)[:4])
    prompt = (
        "Eres un asistente para un juego de lectura para niños de 6 a 8 años con "
        "dislexia. El niño se equivocó separando en sílabas estas palabras: {f}. "
        "Su dificultad es: {d}. Propón {n} palabras en español, sustantivos comunes "
        "que un niño conozca, que tengan esa misma dificultad pero que sean más "
        "fáciles: máximo {m} sílabas. Ejemplos del tipo de palabra: {e}. "
        "Sin nombres propios ni palabras de miedo. Responde SOLO con JSON con esta "
        'forma: {{"palabras": ["palabra1", "palabra2"]}}'
    ).format(f=", ".join(falladas), d=descripcion, n=cantidad * 3,
             m=max_silabas, e=ejemplos)
    cuerpo = json.dumps({
        "model": OLLAMA_MODEL, "prompt": prompt, "format": "json",
        "stream": False, "options": {"temperature": 0.7},
    }).encode("utf-8")
    peticion = urllib.request.Request(
        OLLAMA_URL + "/api/generate", data=cuerpo,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(peticion, timeout=TIEMPO_MAXIMO) as respuesta:
        datos = json.loads(respuesta.read().decode("utf-8"))
    contenido = json.loads(datos.get("response", "{}"))
    palabras = contenido.get("palabras", []) if isinstance(contenido, dict) else []
    return palabras if isinstance(palabras, list) else []


@ia_bp.route("/silabas/refuerzo", methods=["POST"])
@jwt_required()
def refuerzo_silabas():
    """Recibe las palabras en que el niño falló y devuelve palabras de refuerzo.

    Cuerpo esperado:
    {
      "errores": [
        {"palabra": "bicicleta", "respuesta": ["bi", "ci", "ta", "cle"]},
        {"palabra": "tigre"}
      ],
      "cantidad": 5
    }
    "respuesta" (lo que armó el niño) es opcional, pero mejora el análisis.
    """
    datos = request.get_json(silent=True) or {}
    errores = datos.get("errores")
    if not isinstance(errores, list) or not errores:
        return jsonify({"message": "Envía la lista 'errores' con al menos una palabra"}), 400
    try:
        cantidad = min(max(int(datos.get("cantidad", 5)), 1), 10)
    except (TypeError, ValueError):
        return jsonify({"message": "cantidad debe ser un número"}), 400

    analisis = []
    for e in errores[:10]:
        if not isinstance(e, dict) or not isinstance(e.get("palabra"), str):
            continue
        palabra = e["palabra"].strip().lower()
        if not palabra.isalpha():
            continue
        correctas = silabear(palabra)
        respuesta = e.get("respuesta")
        if not (isinstance(respuesta, list) and all(isinstance(x, str) for x in respuesta)):
            respuesta = None
        analisis.append({
            "palabra": palabra,
            "silabas_correctas": correctas,
            "tipo_error": tipo_de_error(correctas, respuesta),
            "dificultades": sorted(dificultades(palabra)),
        })
    if not analisis:
        return jsonify({"message": "No hay palabras válidas en 'errores'"}), 400

    objetivo = _objetivo(analisis)
    mas_corta = min(len(a["silabas_correctas"]) for a in analisis)
    max_silabas = max(2, mas_corta - 1) if mas_corta > 2 else 2
    excluir = {a["palabra"] for a in analisis}

    palabras, fuente = [], "ia"
    try:
        for c in _ollama_refuerzo(sorted(excluir), objetivo, max_silabas, cantidad):
            if isinstance(c, str):
                ok = _es_mas_sencilla(c, objetivo, max_silabas, excluir)
                if ok and ok["palabra"] not in {p["palabra"] for p in palabras}:
                    palabras.append(ok)
            if len(palabras) == cantidad:
                break
    except Exception:
        palabras = []

    if len(palabras) < cantidad:
        fuente = "banco" if not palabras else "ia+banco"
        banco = list(BANCO_REFUERZO.get(objetivo, BANCO_REFUERZO["palabra_larga"]))
        random.shuffle(banco)
        ya = {p["palabra"] for p in palabras} | excluir
        for c in banco:
            ok = _es_mas_sencilla(c, objetivo, max_silabas, ya)
            if ok:
                palabras.append(ok)
                ya.add(ok["palabra"])
            if len(palabras) == cantidad:
                break

    for p in palabras:
        p["opciones"] = opciones_con_distractores(p["silabas"])

    return jsonify({
        "message": "Palabras de refuerzo generadas",
        "data": {
            "objetivo": objetivo,
            "objetivo_descripcion": NOMBRES_DIFICULTAD.get(objetivo, "práctica general"),
            "max_silabas": max_silabas,
            "analisis": analisis,
            "palabras": palabras,
            "fuente": fuente,
        },
    }), 200

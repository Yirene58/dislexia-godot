"""Voz neuronal en español (Piper) para narrar sílabas y palabras (RF5).

Corre en el servidor, sin internet. La misma voz suena igual en la web y en Godot.
Cada audio se genera una vez y se guarda en caché (backend/voces/cache).
"""
import hashlib
import io
import os
import threading
import unicodedata
import wave
from pathlib import Path

CARPETA = Path(__file__).resolve().parent.parent.parent / "voces"
MODELO = os.environ.get("VOZ_MODELO", "es_MX-claude-high")
VELOCIDADES = {"lenta": 1.45, "normal": 1.1}

_voz = None
_lock = threading.Lock()


def disponible():
    return (CARPETA / f"{MODELO}.onnx").exists()


def _cargar():
    global _voz
    if _voz is None:
        from piper import PiperVoice
        _voz = PiperVoice.load(str(CARPETA / f"{MODELO}.onnx"))
    return _voz


def limpiar_texto(texto):
    """Solo letras del español, espacios y puntuación simple; máximo 80 caracteres."""
    texto = unicodedata.normalize("NFC", str(texto)).strip().lower()[:80]
    permitidos = set("abcdefghijklmnñopqrstuvwxyzáéíóúü ,.¡!¿?")
    return "".join(c for c in texto if c in permitidos).strip()


def audio_wav(texto, velocidad="normal"):
    """Devuelve los bytes WAV del texto (desde caché si ya existe)."""
    texto = limpiar_texto(texto)
    if not texto:
        raise ValueError("texto vacío")
    escala = VELOCIDADES.get(velocidad, VELOCIDADES["normal"])
    clave = hashlib.sha1(f"{MODELO}|{escala}|{texto}".encode("utf-8")).hexdigest()
    cache = CARPETA / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    archivo = cache / f"{clave}.wav"
    if archivo.exists():
        return archivo.read_bytes()
    from piper import SynthesisConfig
    with _lock:
        voz = _cargar()
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as w:
            voz.synthesize_wav(texto, w, syn_config=SynthesisConfig(length_scale=escala))
    datos = buffer.getvalue()
    archivo.write_bytes(datos)
    return datos

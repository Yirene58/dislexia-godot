#!/bin/bash
# Instala la voz neuronal en español (Piper) en el backend: ruta GET /api/voz (RF5).
# Uso (en la terminal del Codespace, carpeta principal):  bash instalar_voz.sh
set -e
cd /workspaces/dislexia-godot
MODELO=es_MX-claude-high
URL=https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/es/es_MX/claude/high

echo "1/5 Copiando archivos de la voz..."
echo "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" | base64 -d | tar xzf -

echo "2/5 Registrando la ruta /api/voz..."
python - <<'PY'
p = "backend/app/__init__.py"
s = open(p, encoding="utf-8-sig").read()
if "voz_bp" not in s:
    i = s.rindex("    return app")
    s = s[:i] + "    from app.routes.voz_routes import voz_bp\n    app.register_blueprint(voz_bp)\n\n" + s[i:]
    open(p, "w", encoding="utf-8").write(s)
PY
python - <<'PY'
# requirements.txt viene en UTF-16: se agrega piper-tts respetando su codificación
p = "backend/requirements.txt"
crudo = open(p, "rb").read()
cod = "utf-16" if crudo[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8"
texto = crudo.decode(cod)
if "piper-tts" not in texto:
    texto = texto.rstrip() + "\npiper-tts==1.8.0\n"
    open(p, "wb").write(texto.encode(cod))
PY
grep -q "^backend/voces/" .gitignore 2>/dev/null || printf '\nbackend/voces/\n' >> .gitignore

echo "3/5 Instalando Piper (puede tardar 1-2 minutos)..."
pip install -q piper-tts==1.8.0

echo "4/5 Descargando la voz en español latinoamericano (~110 MB)..."
mkdir -p backend/voces
[ -f backend/voces/$MODELO.onnx ] || curl -fL --progress-bar -o backend/voces/$MODELO.onnx "$URL/$MODELO.onnx"
[ -f backend/voces/$MODELO.onnx.json ] || curl -fsSL -o backend/voces/$MODELO.onnx.json "$URL/$MODELO.onnx.json"

echo "5/5 Probando la voz..."
(cd backend && python - <<'PY'
from app.services import voz
datos = voz.audio_wav("pe, lo, ta. pelota", "lenta")
print("Voz funcionando:", len(datos), "bytes de audio")
PY
)
echo ""
echo "Listo. Reinicia el backend para que tome la ruta nueva:"
echo "  pkill -f 'python run.py'; (cd backend && nohup python run.py > /tmp/backend.log 2>&1 &)"
echo "Comprueba con:  curl localhost:5000/api/voz/estado"

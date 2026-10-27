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

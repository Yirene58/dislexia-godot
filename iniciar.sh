#!/bin/bash
# Prende backend, Ollama (si está instalado) y frontend
cd /workspaces/dislexia-godot

if command -v ollama > /dev/null; then
  nohup ollama serve > /tmp/ollama.log 2>&1 &
  echo "Ollama prendido"
fi

(cd backend && nohup python run.py > /tmp/backend.log 2>&1 &)
echo "Backend prendido"

cd frontend
npm run dev
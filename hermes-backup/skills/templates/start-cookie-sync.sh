#!/bin/bash
# Auto-start Cookie Sync Webhook
#
# ⚠️ Executed inside Hermes Docker container — use /app/venv/bin/python3.
#    Global python3 does NOT have fastapi/uvicorn.
#
# Port: 9999 (port 8000 is occupied by another app on this server).
#
# Non-destructive: does NOT pkill existing instances. Checks health
# first, only starts if nothing is serving.
#
# Usage: bash ~/.hermes/scripts/start-cookie-sync.sh

cd /workspace/hermes-browser-sync
PYTHON=/app/venv/bin/python3
PORT="${PORT:-9999}"

# Already healthy? Skip (nevere kill a working instance).
if curl -s -o /dev/null http://localhost:$PORT/health 2>/dev/null; then
    echo "[cookie-sync] Already healthy on :$PORT"
    exit 0
fi

# Read token from .env
if [ -z "$HERMES_API_KEY" ] && [ -f .env ]; then
    export HERMES_API_KEY=$(grep HERMES_API_KEY .env | head -1 | cut -d= -f2)
fi
export PORT

# Start fresh (nothing was listening)
nohup $PYTHON main.py > /tmp/fastapi-webhook.log 2>&1 &
sleep 2

if curl -s -o /dev/null http://localhost:$PORT/health; then
    echo "[cookie-sync] OK on :$PORT"
else
    echo "[cookie-sync] FAILED — check /tmp/fastapi-webhook.log"
    tail -5 /tmp/fastapi-webhook.log
fi
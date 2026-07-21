#!/bin/bash
# Cookie Sync Daemon — fully detached from Hermes session
# Usage: bash ~/.hermes/scripts/start-cookie-sync.sh

PYTHON=/app/venv/bin/python3
SCRIPT=~/.hermes/scripts/cookie-sync-webhook.py
CF=/home/hermeswebui/.local/bin/cloudflared

# --- Cookie-Sync Server (stdlib, no deps) ---
if ! curl -s -o /dev/null http://localhost:9999/health 2>/dev/null; then
    echo "[daemon] Starting cookie-sync on :9999..."
    setsid env COOKIE_SYNC_TOKEN=7jJt8VW7OvdbhgMiJ5bVy9BWZOtJHMBBC1p82zIatmQ \
        COOKIE_SYNC_PORT=9999 \
        $PYTHON "$SCRIPT" > /tmp/cookie-sync.log 2>&1 &
    sleep 2
    if curl -s -o /dev/null http://localhost:9999/health 2>/dev/null; then
        echo "[daemon] cookie-sync OK"
    else
        echo "[daemon] cookie-sync FAILED"
        cat /tmp/cookie-sync.log | tail -5
    fi
else
    echo "[daemon] cookie-sync already running"
fi

# --- Cloudflared Tunnel ---
if ! curl -s -o /dev/null "http://localhost:9999/health" 2>/dev/null; then
    echo "[daemon] cookie-sync not reachable, skip tunnel"
    exit 1
fi

# check if cloudflared is actually working (not just process alive)
TUNNEL_OK=false
if pgrep -f "cloudflared tunnel" >/dev/null 2>&1; then
    # check if tunnel log has a URL and no recent errors
    if grep -q "trycloudflare.com" /tmp/cloudflared.log 2>/dev/null; then
        URL=$(grep -o 'https://[^ ]*trycloudflare.com' /tmp/cloudflared.log 2>/dev/null | tail -1)
        if curl -s -o /dev/null --connect-timeout 3 "$URL/health" 2>/dev/null; then
            TUNNEL_OK=true
            echo "[daemon] Tunnel OK: $URL"
        fi
    fi
fi

if ! $TUNNEL_OK; then
    echo "[daemon] Restarting cloudflared tunnel..."
    pkill -f "cloudflared tunnel" 2>/dev/null
    sleep 2
    cd /tmp && setsid $CF tunnel --url http://localhost:9999 > /tmp/cloudflared.log 2>&1 &
    for i in $(seq 1 20); do
        URL=$(grep -o 'https://[^ ]*trycloudflare.com' /tmp/cloudflared.log 2>/dev/null | head -1)
        if [ -n "$URL" ]; then
            echo "$URL" > /tmp/cookie-sync-url.txt
            echo "[daemon] Tunnel OK: $URL"
            break
        fi
        sleep 1
    done
    if [ -z "$URL" ]; then
        echo "[daemon] Tunnel FAILED"
        tail -5 /tmp/cloudflared.log
    fi
fi

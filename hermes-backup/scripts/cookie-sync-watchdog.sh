#!/bin/bash
# Cookie-Sync Tunnel Watchdog
# Checks: server alive? tunnel alive? If not, restart and notify.
# Silent when everything is healthy.
# NOTE: pgrep/ps not available in this container — use /proc/*/cmdline.

PORT=9999
CLOUDFLARED="$HOME/.local/bin/cloudflared"
PYTHON=/app/venv/bin/python3
SCRIPT="$HOME/.hermes/scripts/cookie-sync-webhook.py"
URLFILE="/tmp/cookie-sync-url.txt"
LOGFILE="$HOME/.hermes/logs/cookie-sync-watchdog.log"
TUNNEL_LOG="/tmp/cloudflared-cookiesync.log"

mkdir -p "$(dirname "$LOGFILE")"
log() { echo "[$(date -Iseconds)] $*" >> "$LOGFILE"; }

# Check if cloudflared tunnel for THIS port is running
tunnel_running() {
    for pid in $(ls /proc/ 2>/dev/null | grep -E '^[0-9]+$'); do
        cmdline=$(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ')
        if echo "$cmdline" | grep -q "cloudflared tunnel.*localhost:$PORT"; then
            return 0
        fi
    done
    return 1
}

# Kill all cloudflared tunnel processes for THIS port
kill_tunnels() {
    for pid in $(ls /proc/ 2>/dev/null | grep -E '^[0-9]+$'); do
        cmdline=$(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ')
        if echo "$cmdline" | grep -q "cloudflared tunnel.*localhost:$PORT"; then
            kill "$pid" 2>/dev/null
        fi
    done
}

# --- 1. Check cookie-sync server (port 9999) ---
if ! curl -sf http://localhost:$PORT/health --connect-timeout 3 >/dev/null 2>&1; then
    log "Server DOWN on :$PORT, restarting..."
    pkill -f "cookie-sync-webhook.py" 2>/dev/null
    sleep 1
    setsid env COOKIE_SYNC_TOKEN=7jJt8VW7OvdbhgMiJ5bVy9BWZOtJHMBBC1p82zIatmQ \
        COOKIE_SYNC_PORT=$PORT \
        "$PYTHON" "$SCRIPT" > /tmp/cookie-sync.log 2>&1 &
    sleep 3
    if ! curl -sf http://localhost:$PORT/health --connect-timeout 3 >/dev/null 2>&1; then
        log "Server FAILED to restart"
        echo "Cookie-sync server DOWN on :$PORT — noti failed"
        exit 0
    fi
    log "Server restarted OK"
fi

# --- 2. Check cloudflared tunnel process ---
if tunnel_running && [ -s "$URLFILE" ]; then
    exit 0  # healthy, silent
fi

# --- 3. No tunnel or no URL — start fresh ---
log "Tunnel missing, starting cloudflared for :$PORT..."
kill_tunnels
sleep 2

nohup "$CLOUDFLARED" tunnel --url "http://localhost:$PORT" > "$TUNNEL_LOG" 2>&1 &
sleep 15

NEW_URL=$(grep -o "https://[a-z0-9.-]*\.trycloudflare\.com" "$TUNNEL_LOG" 2>/dev/null | tail -1)

if [ -z "$NEW_URL" ]; then
    log "Failed to get tunnel URL"
    echo "Cloudflared tunnel baraye port $PORT nashod. Log: $TUNNEL_LOG"
    exit 0
fi

echo "$NEW_URL" > "$URLFILE"
log "New tunnel URL: $NEW_URL"

echo "Cookie-sync tunnel adrese jadid gereft:

URL: $NEW_URL/api/browser-sync
API Key: 7jJt8VW7OvdbhgMiJ5bVy9BWZOtJHMBBC1p82zIatmQ

In URL ro to CacheCat setups kon."

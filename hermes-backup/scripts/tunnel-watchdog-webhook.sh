#!/bin/bash
# Webhook Tunnel Watchdog — no_agent=True cron script
# Checks cloudflared tunnel to port 8644, restarts if dead.
# Only outputs something (to be sent to Telegram) when URL changes.

CLOUDFLARED="$HOME/.local/bin/cloudflared"
URLFILE="/tmp/webhook-tunnel-url.txt"
LOGFILE="$HOME/.hermes/logs/webhook-tunnel.log"
OLDPORT_LOG="/tmp/cloudflared_webhook_new.log"
PORT=8644

mkdir -p "$(dirname "$LOGFILE")"

log() { echo "[$(date -Iseconds)] $*" >> "$LOGFILE"; }

# Check if cloudflared is running for this port
if pgrep -f "cloudflared.*localhost:$PORT" >/dev/null 2>&1; then
    # Tunnel up — check if URL is reachable
    OLD_URL=$(cat "$URLFILE" 2>/dev/null)
    if [ -n "$OLD_URL" ] && curl -sf "$OLD_URL/health" >/dev/null 2>&1; then
        # All good, silent exit
        exit 0
    fi
    # Tunnel process exists but health fails — kill and restart
    log "Tunnel unhealthy, restarting..."
    pkill -f "cloudflared.*localhost:$PORT" 2>/dev/null
    sleep 2
fi

# Start new tunnel
log "Starting cloudflared tunnel for :$PORT..."
nohup "$CLOUDFLARED" tunnel --url "http://localhost:$PORT" > "$OLDPORT_LOG" 2>&1 &
CF_PID=$!

# Wait for URL
sleep 12
NEW_URL=$(grep -o "https://[a-z0-9.-]*\.trycloudflare\.com" "$OLDPORT_LOG" 2>/dev/null | head -1)

if [ -z "$NEW_URL" ]; then
    log "Failed to get tunnel URL"
    echo "❌ Webhook tunnel failed to start for port $PORT"
    exit 1
fi

echo "$NEW_URL" > "$URLFILE"
log "New tunnel URL: $NEW_URL"

# Send new URL to Telegram
echo "🔄 Webhook tunnel renewed

URL: $NEW_URL/webhooks/test-webhook
Port: $PORT (Hermes Webhook)"

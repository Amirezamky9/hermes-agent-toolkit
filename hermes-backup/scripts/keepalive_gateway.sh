#!/bin/bash
# Gateway keepalive - checks if gateway is running, restarts if not
# Run via cron: * * * * * /home/hermeswebui/.hermes/scripts/keepalive_gateway.sh

export HERMES_HOME=/home/hermeswebui/.hermes
export PYTHONPATH=/home/hermeswebui/.hermes/hermes-agent

PID_FILE="$HERMES_HOME/gateway.pid"
LOG_FILE="$HERMES_HOME/logs/gateway.log"
RESTART_LOG="$HERMES_HOME/logs/keepalive.log"

is_gateway_running() {
    # Check PID file
    if [ -f "$PID_FILE" ]; then
        PID=$(python3 -c "import json; print(json.load(open('$PID_FILE'))['pid'])" 2>/dev/null)
        if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
            return 0  # running
        fi
    fi
    # Fallback: check if any hermes_cli gateway process exists
    if pgrep -f "hermes_cli.*gateway" >/dev/null 2>&1; then
        return 0
    fi
    return 1  # not running
}

if ! is_gateway_running; then
    echo "[$(date -Iseconds)] Gateway not running — restarting..." >> "$RESTART_LOG"
    cd "$HERMES_HOME"
    nohup python3 -m hermes_cli.main gateway run >> "$LOG_FILE" 2>&1 &
    disown
    echo "[$(date -Iseconds)] Gateway restarted (PID $!)" >> "$RESTART_LOG"
    # Trim log to last 500 lines
    tail -500 "$RESTART_LOG" > "${RESTART_LOG}.tmp" && mv "${RESTART_LOG}.tmp" "$RESTART_LOG"
fi

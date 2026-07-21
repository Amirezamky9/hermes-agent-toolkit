# Cookie-Sync Webhook — Operations Reference

## Architecture

```
Browser extension → Cloudflare Tunnel → localhost:9999 → cookie-sync-webhook.py
                                                      ↓
                                              ~/.agent-reach/config.yaml
                                              (cookies saved to agent-reach config)
```

## Key Files

| File | Purpose |
|------|---------|
| `~/.hermes/scripts/cookie-sync-webhook.py` | stdlib Python HTTP server (port 9999). No FastAPI/deps. |
| `~/.hermes/scripts/start-cookie-sync.sh` | Daemon starter — launches server + cloudflared tunnel. |
| `~/.hermes/logs/cookie-sync.log` | Server logs |
| `~/.hermes/logs/cookie-sync-watchdog.log` | Tunnel watchdog restart logs |
| `/tmp/cookie-sync-url.txt` | Current tunnel URL (written by startup script) |

## Auth

- **Token**: set via `COOKIE_SYNC_TOKEN` env var in startup script.
- **Port**: `COOKIE_SYNC_PORT=9999` (default).
- **Health check**: `curl -s http://localhost:9999/health`

## Startup Sequence

```bash
# 1. Start cookie-sync server + cloudflared tunnel
bash ~/.hermes/scripts/start-cookie-sync.sh

# 2. Verify health
curl -s http://localhost:9999/health

# 3. Check tunnel URL
cat /tmp/cookie-sync-url.txt
# Output: https://<random>.trycloudflare.com

# 4. Verify tunnel is reachable (use URL from step 3)
curl -s "<tunnel-url>/health"
```

## Recovery — Tunnel Keeps Dying

The cloudflared quick tunnel generates a new URL on each restart. If the
watchdog keeps restarting, check:

```bash
# Is cloudflared installed?
which cloudflared || ls ~/.local/bin/cloudflared

# Check watchdog log for error patterns
tail -50 ~/.hermes/logs/cookie-sync-watchdog.log

# Manual restart (kills old tunnel, starts fresh)
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 2
bash ~/.hermes/scripts/start-cookie-sync.sh
```

## Recovery — Port 9999 Already in Use

```bash
# Find what's using the port
lsof -i :9999 || ss -tlnp | grep 9999

# Kill old process if safe
kill $(lsof -t -i :9999) 2>/dev/null
```

## Relationship to Agent-Reach

This webhook is the **cookie delivery mechanism** for agent-reach's
login-backed platforms (Twitter, Reddit, etc.). The flow:

1. User exports cookies from browser (via Cookie-Editor extension)
2. Cookies POST to this webhook (via cloudflared tunnel URL)
3. Webhook saves cookies to `~/.agent-reach/config.yaml`
4. agent-reach tools (twitter-cli, rdt-cli) read from that config

The tunnel URL changes on restart — the user must receive the new URL
each time (typically via Telegram message after startup).

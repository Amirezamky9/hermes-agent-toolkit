---
name: webhook-trigger
description: Create webhook triggers using Hermes built-in Webhook Platform (port 8644, HMAC-SHA256 auth). For when user says "webhook trigger" or "webhook بزن" — use THIS skill, not the FastAPI cookie-sync.
version: 1.1.0
---

# Webhook Trigger — Hermes Built-in Platform

## Two Systems — Don't Confuse

| System | Port | Auth | Use for |
|--------|------|------|---------|
| **Hermes Webhook Platform** ← THIS | 8644 | HMAC-SHA256 | GitHub, GitLab, Stripe, CI/CD, custom scripts |
| Cookie-Sync (stdlib Python) | 9999 | Bearer Token | CacheCat browser extension only |

| Detail | Hermes Webhook Platform | Cookie-Sync |
|--------|------------------------|-------------|
| Script | built-in (Gateway) | `~/.hermes/scripts/cookie-sync-webhook.py` |
| Startup | auto (Gateway) | `~/.hermes/scripts/start-cookie-sync.sh` (manual or cron) |
| Dependencies | none (built-in) | **zero** (stdlib http.server, no FastAPI) |
| Watchdog | cron `webhook-tunnel-watchdog` (port 8644) | cron `cookie-sync-watchdog` (port 9999, every 30m) |
| Tunnel URL file | `/tmp/webhook-tunnel-url.txt` | `/tmp/cookie-sync-url.txt` |

**When user says "webhook بزن" or "webhook trigger" → use port 8644, NOT port 9999.**

### Cookie-sync (port 9999) watchdog
Cron job `cookie-sync-watchdog` (`f7a2f52fde45`) runs every 30m, `no_agent=True` script.
Checks: server alive on :9999? cloudflared tunnel process running? URL file set?
If anything down → restarts server and/or tunnel, sends new URL to Telegram.
If healthy → silent (empty stdout, nothing sent).
Script: `~/.hermes/scripts/cookie-sync-watchdog.sh`

For full cookie-sync architecture (endpoints, persistence, files), see [`references/cookie-sync-architecture.md`](skill_view://webhook-trigger/references/cookie-sync-architecture.md).

## Current State

| Item | Value |
|------|-------|
| Webhook platform | ✅ Enabled in `config.yaml` (port 8644) |
| Gateway | ✅ Running |
| External URL | `https://keyboard-endangered-cable-engineering.trycloudflare.com/webhooks/<name>` |
| Tunnel watchdog | Cron job every 12h, delivers new URL via Telegram if tunnel renews |

## Create a New Webhook Trigger

Run in terminal:

```bash
export PATH=$PATH:/app/venv/bin
hermes webhook subscribe <name> \
  --prompt "Your prompt with {payload.field1} and {payload.field2}" \
  --description "What this webhook does" \
  --deliver origin
```

- `--deliver origin` → response comes back to this chat
- `--deliver telegram:943724562` → send to user's Telegram
- `--events "event1,event2"` → filter by event type (optional, omit for all)

## How External Client Calls It

```bash
SECRET="<secret-from-create-output>"
PAYLOAD='{"field1":"value1","field2":"value2"}'
SIG=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $2}')

curl -X POST https://<tunnel-url>/webhooks/<name> \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$SIG" \
  -d "$PAYLOAD"
```

## List / Remove / Test

```bash
hermes webhook list
hermes webhook remove <name>
hermes webhook test <name> --payload '{"key":"val"}'
```

## Manage the Tunnel

- Tunnel runs as background process (proc_7f7c1048fe20)
- Cron job `f7a2f52fde45` (webhook-tunnel-watchdog) checks every 12h
- If tunnel dies, script kills & restarts, delivers new URL to Telegram
- Tunnel URL: stored in `/tmp/webhook-tunnel-url.txt`

## External URL

The external URL changes if the tunnel restarts:
- If current tunnel dies and renews, the new URL arrives in Telegram
- To check now: `cat /tmp/webhook-tunnel-url.txt` or check the live background process

## Managing Non-Webhook Tunnels

The same `cloudflared tunnel --url` pattern works for any HTTP service, not just webhooks.
To expose any local port:

```bash
cloudflared tunnel --url http://localhost:<PORT> 2>&1
# Extract URL from output: https://<random>.trycloudflare.com
```

### ⚠️ WebSocket Does NOT Work From Browsers Through cloudflared Quick Tunnel

Cloudflare Quick Tunnel (`trycloudflare.com`) **fails WebSocket upgrade from mobile/desktop browsers** — the page loads (HTTP 200) but WebSocket shows "اتصال قطع شد" / `ERR_CONNECTION_REFUSED`. Server-side Node.js WebSocket clients DO connect fine. This is a known limitation of Quick Tunnel's HTTP/2 WebSocket handling in browsers.

**For apps that need WebSocket (games, chat, real-time):** Use `localtunnel` instead:

```bash
npx --yes localtunnel --port 3000
# Output: your url is: https://<name>.loca.lt
# First visit shows "Click to Continue" page — user must click through once
# WebSocket works from browsers ✅
```

**Decision matrix:**
| Need | Tool | WebSocket from browser? | Notes |
|------|------|------------------------|-------|
| HTTP-only webhooks/APIs | `cloudflared tunnel --url` | N/A | Fastest, most reliable |
| WebSocket apps (games, chat) | `npx localtunnel --port` | ✅ Yes | Splash page on first visit |
| Both HTTP + WebSocket | `npx localtunnel --port` | ✅ Yes | Splash page on first visit |
| **Anything, guaranteed** | **HTTP Polling + cloudflared** | N/A | **Most reliable** — see below |

**localtunnel caveat:** First visit shows a "Click to Continue" interstitial page. Users must click through once. After that, direct access works. Sometimes this page blocks entirely (user reports "باز نمیشه").

### HTTP Polling — The Nuclear Option (Most Reliable)
When both cloudflared AND localtunnel fail for real-time apps, **rewrite the client to use HTTP Polling instead of WebSocket**. Works through any proxy/tunnel/firewall.

**Pattern:**
- Client sends `POST /api/action` with game events
- Client polls `POST /api/poll` every 1-2 seconds for state updates
- Server maintains game state in memory, responds to each poll with current state
- No WebSocket needed — pure HTTP POST/GET

**Server pattern (Node.js):**
```javascript
// Polling endpoint — client calls this every 1-2s
app.post('/api/poll', (req, res) => {
  const state = getGameState(req.body.roomId, req.body.playerId);
  res.json({ ok: true, state });
});
```

**Client pattern:**
```javascript
async function poll() {
  const r = await fetch('/api/poll', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({roomId, playerId}) });
  const data = await r.json();
  if (data.ok && data.state) render(data.state);
  setTimeout(poll, 1500); // poll every 1.5s
}
```

**Tradeoffs:** Adds ~1.5s latency (vs real-time WebSocket). Fine for turn-based games, not for action games. Uses more HTTP requests but each is tiny.

## Hermes ↔ n8n Integration

For bidirectional webhook integration between Hermes and n8n (e.g., daily routine bots, AI-powered workflows), see [`references/hermes-n8n-integration.md`](references/hermes-n8n-integration.md). Covers n8n→Hermes (HTTP Request + HMAC), Hermes→n8n (POST to n8n webhook), and a daily routine bot architecture example.

## ⚠️ Key Rules

- NEVER create a webhook on port 9999 (that's the FastAPI cookie-sync, different auth)
- NEVER use Bearer Token with the webhook platform — it only accepts HMAC-SHA256
- `hermes webhook subscribe` is the ONLY way to create routes on port 8644
- Always use `--deliver origin` unless user specifies another destination
- When user says "ساده و خام" → just use tunnel, don't propose Traefik/Caddy unless asked

## ⚠️ Pitfalls

### Container Environment: No `pgrep` / `ps`
This container has **neither `pgrep` nor `ps`**. Any watchdog or health-check script must use `/proc` directly:
```bash
for pid in $(ls /proc/ 2>/dev/null | grep -E '^[0-9]+$'); do
    cmdline=$(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ')
    if echo "$cmdline" | grep -q "PATTERN"; then echo "found PID $pid"; fi
done
```
`pkill -f "cloudflared.*localhost:PORT"` fails silently because `/proc/*/cmdline` is null-separated and glob `.*` doesn't match across null bytes. Always iterate `/proc` explicitly. Killing processes from inside a terminal call can kill the parent shell too — write a helper script to `/tmp/` and execute it separately.

### Persistent Services Must Live Outside `/workspace`
The user periodically cleans `/workspace` to free space. **Never store persistent service code inside `/workspace`.** Use `~/.hermes/scripts/` for anything that must survive cleanup.

### Cloudflare Quick Tunnel `ERR_CONNECTION_REFUSED`
Cloudflare Quick Tunnel URLs can return `ERR_CONNECTION_REFUSED` from the client even when
server-side `curl https://<tunnel-url>` returns 200. This is a recurring pattern.

**Causes (in order of likelihood):**
1. **DNS caching** — browser cached a previous dead tunnel URL
2. **ISP blocking** — some ISPs block trycloudflare.com domains
3. **Tunnel process died** — Quick Tunnels are ephemeral, no uptime guarantee
4. **Protocol mismatch** — QUIC sometimes fails; try `--protocol http2`

**Fix sequence (do ALL of these before declaring it broken):**
1. Kill the old tunnel process, restart `cloudflared tunnel --url http://localhost:<PORT>`
2. Verify from server: `curl -s -o /dev/null -w "%{http_code}" https://<new-url>`
3. If 200 from server but client still fails:
   - Open in **Incognito/Private** window (kills DNS cache)
   - **Flush DNS cache**: `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)
   - Switch from **WiFi to mobile data** (or vice versa)
4. If still failing after 2 min, the Quick Tunnel may have been rate-limited — wait 30s and restart
5. Quick Tunnel URLs change on every restart. Always give the user the LATEST URL.

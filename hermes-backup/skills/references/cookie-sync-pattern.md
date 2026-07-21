# CacheCat Cookie Sync Pattern

## Overview

CacheCat is a Chrome extension (chinmay29hub/CacheCat) that reads browser storage and sends cookies to a webhook server. The server then updates tool credentials automatically.

## Architecture

```
Chrome (CacheCat) → HTTP POST → webhook.py → credential files → tools
```

## Webhook Server

Location: `~/.hermes/scripts/cookie-sync-webhook.py`

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/` | Receive cookies |
| POST | `/api/browser-sync` | Same (extension compat) |
| POST | `/api/test-connection` | Connection test |
| GET | `/health` | Health check |

### Authentication

Token-based: `Authorization: Bearer <TOKEN>` or URL path `/<TOKEN>`.

### Cookie Flow

1. Extension sends `{domain, cookies[]}` payload
2. Server saves raw JSON to `~/.agent-reach/cookies/<domain>.json`
3. Server merges into `hermes-cookies.json` (master store)
4. Server updates tool-specific credentials:
   - Twitter: `twitter.env` (AUTH_TOKEN, CT0)
   - Reddit: `~/.config/rdt-cli/credential.json`
   - YouTube: `youtube-cookies.txt` (Netscape format)
   - Xueqiu: `xueqiu.json`

## Setup

```bash
# Generate token
export COOKIE_SYNC_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Start server
python3 ~/.hermes/scripts/cookie-sync-webhook.py &

# Start tunnel (for external access)
cloudflared tunnel --url http://localhost:9999 &

# Get tunnel URL
grep 'trycloudflare.com' /tmp/cloudflared.log
```

## Pitfalls

### Grok.com cookies not captured

Cloudflare blocks grok.com cookies even with valid SSO. The `sso` and `sso-rw` cookies are HttpOnly and Cloudflare's challenge prevents the webhook from reaching grok.com. Only analytics/device cookies are captured.

**Workaround:** Use xAI API (`console.x.ai`) instead of browser cookies for Grok access.

### YouTube cookies format

YouTube requires Netscape cookie format for yt-dlp. The webhook auto-converts, but verify:

```bash
head -5 ~/.agent-reach/cookies/youtube-cookies.txt
# Should show: # Netscape HTTP Cookie File
```

### Cookie freshness

Cookies expire. Check age:

```bash
ls -la ~/.agent-reach/cookies/*.json
# Files > 7 days old need re-sync
```

## Tunnel Setup (Cloudflare)

```bash
# Install cloudflared
pipx install cloudflared

# Start tunnel
cloudflared tunnel --url http://localhost:9999 > /tmp/cloudflared.log 2>&1 &

# Get URL
grep 'trycloudflare.com' /tmp/cloudflared.log
```

# Cookie-Sync Architecture

## Overview
A stdlib-Python HTTP server (no FastAPI, no dependencies) that receives browser cookies from the CacheCat browser extension and persists them. Lives entirely under `~/.hermes/scripts/` — safe from `/workspace` cleanup.

## Files

| File | Purpose |
|------|---------|
| `~/.hermes/scripts/cookie-sync-webhook.py` | The server (182 lines, stdlib only) |
| `~/.hermes/scripts/cookie-sync.env` | Environment vars (token + port) |
| `~/.hermes/scripts/start-cookie-sync.sh` | Startup script (server + cloudflared tunnel) |

## Endpoints

| Path | Method | Purpose |
|------|--------|---------|
| `/api/browser-sync` | POST | Receive cookies (main CacheCat endpoint) |
| `/api/test-connection` | POST | Extension test button |
| `/health` | GET | Health check |

## Auth
Bearer token in `COOKIE_SYNC_TOKEN` env var. Sent as `Authorization: Bearer <token>`.

## Persistence
Cookies are stored in `~/.agent-reach/cookies/`:
- `hermes-cookies.json` — master store (merged, deduplicated by `name|domain`)
- `twitter.env` — Twitter/X credentials for twitter-cli
- `<domain>.json` — raw payload per domain

## Watching for cookie updates
Run the following to check the last cookie received per domain:
```bash
ls -lt ~/.agent-reach/cookies/*.json
```

## Automatic Watchdog
Cron job `cookie-sync-watchdog` (id `f7a2f52fde45`) runs every 30m with `no_agent=True`:
- Script: `~/.hermes/scripts/cookie-sync-watchdog.sh`
- Checks: server alive? tunnel process running? URL file set?
- If down → restarts and sends new URL to Telegram
- If healthy → silent (nothing sent)

To restart manually:
```bash
bash ~/.hermes/scripts/start-cookie-sync.sh
```

## Port Conflicts
The FastAPI version was at `/workspace/hermes-browser-sync/main.py` — that directory no longer exists. Only one cookie-sync server should run on port 9999.
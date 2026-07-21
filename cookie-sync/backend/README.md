# Hermes Backend Example

FastAPI backend for receiving cookies from the Hermes Browser Sync extension.

## Purpose

This backend runs on the Hermes side and receives cookies from the client-side Chrome extension. It converts those cookies into Playwright `storage_state.json` so Hermes can reuse authenticated sessions.

## Files

- `main.py` — FastAPI app
- `requirements.txt` — Python dependencies
- `.env.example` — environment template

## Setup

```bash
cd cookie-sync/backend
cp .env.example .env
pip install -r requirements.txt
python main.py
```

## Environment variables

- `HERMES_API_KEY` — shared secret between extension and backend
- `STORAGE_STATE_PATH` — where Playwright state is written
- `BACKEND_HOST` — bind host
- `BACKEND_PORT` — bind port

## API

### `POST /api/browser-sync`
Receives cookies from the extension and writes them to storage state.

### `POST /api/test-connection`
Simple connectivity test.

### `GET /health`
Health check.

## Cloudflare / remote access

If the Hermes backend is not directly reachable from the user’s computer, place it behind a secure HTTPS tunnel such as Cloudflare Tunnel.

Example:

```bash
cloudflared tunnel --url http://localhost:8000
```

Then set the extension API URL to the tunnel URL.

## Security

- Keep the API key secret
- Use HTTPS or a trusted tunnel
- Do not expose this endpoint without auth
- Never commit `storage_state.json`

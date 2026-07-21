# Hermes Toolkit Packaging Notes

## Scope

This repository packages the full Hermes research stack into one installable repo:
- `cookie-sync/client/` — CacheCat-based Chrome extension
- `cookie-sync/backend/` — FastAPI webhook server
- `cookie-sync/hermes-browser-sync.config.json` — Hermes-side integration template
- `telegram-toolkit/` — Telegram automation toolkit
- `research/` — token-compressed multi-platform research scripts
- `skills/` — Hermes skills + references

## Recommended install order

1. Clone repo
2. Install Python deps
3. Install Hermes skills into `~/.hermes/skills/`
4. Copy research scripts into `~/.hermes/scripts/`
5. Build `cookie-sync/client/` and load `dist/` in Chrome
6. Run `cookie-sync/backend/main.py`
7. Point client to backend URL + Bearer token
8. Configure Hermes Playwright / storage_state path

## Client-side cookie sync

- Build from source with `npm install && npm run build`
- Load unpacked extension from `cookie-sync/client/dist/`
- Configure sync domains in the Hermes Sync dashboard tab
- Add `google.com`, `x.com`, `notebooklm.google.com`, etc. only if the user asked for them

## Backend-side cookie sync

- Backend uses FastAPI and writes Playwright `storage_state.json`
- Endpoint shape:
  - `POST /api/browser-sync`
  - `POST /api/test-connection`
  - `GET /health`
- If direct access is not possible, use Cloudflare Tunnel or another HTTPS front door
- Keep API key secret; do not commit `.env` or `storage_state.json`

## Hermes-side wiring

- Hermes reads synced storage state via Playwright `storage_state.json`
- `cookie-sync/hermes-browser-sync.config.json` is a template; copy it into the Hermes project root or equivalent integration root
- Keep the backend path and Hermes storage path aligned

## Git hygiene and contributors

- Use `noreply@...` style emails when committing generated packaging repos to avoid accidental contributor attribution to a real user account
- Before publish, scan the entire tree and also the copied Hermes skills for secrets, session files, API keys, phone numbers, and storage state
- Never include `node_modules/`, `.session`, `.env`, or real cookie dumps in the repo

## Reference pointer

See also: `references/hermes-toolkit-repo.md` and `references/cookie-sync-pattern.md`.

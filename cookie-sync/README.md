# Cookie Sync

The cookie sync system is split into two parts:

- `cookie-sync/client/` — CacheCat-based Chrome extension installed on the user’s computer
- `cookie-sync/backend/` — FastAPI webhook server running on the Hermes side
- `cookie-sync/hermes-browser-sync.config.json` — Hermes-side config template

## Recommended flow

1. Build the client extension from `cookie-sync/client/`
2. Install the extension in Chrome
3. Run the backend in `cookie-sync/backend/`
4. Configure the extension with the backend URL + API key
5. Add sync domains
6. Use Hermes/Playwright with the synced `storage_state.json`

## Client

See `cookie-sync/client/README.md`.

## Backend

See `cookie-sync/backend/README.md`.

## Hermes integration config

Copy `cookie-sync/hermes-browser-sync.config.json` into the Hermes project root.

## Security

Do not commit real cookies, tokens, `.env`, or `storage_state.json`.

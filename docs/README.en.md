# Hermes Toolkit Documentation (English)

This repository includes three major parts:

1. **Cookie Sync** — CacheCat-based Chrome extension on the user’s machine + Hermes FastAPI backend
2. **Telegram Toolkit** — Telethon-based search/download/monitor toolkit
3. **Research Tools** — Agent-Reach scripts and Hermes skills for 16+ platforms

## Start here

- [Installation Guide](installation.md)
- [Cookie Sync Overview](../cookie-sync/README.md)
- [Cookie Sync Client](../cookie-sync/client/README.md)
- [Cookie Sync Backend](../cookie-sync/backend/README.md)
- [Telegram Toolkit](../telegram-toolkit/README.md)
- [Research Tools](../research/README.md)

## File layout

- `cookie-sync/client/` — browser extension users install in Chrome
- `cookie-sync/backend/` — webhook backend that stores cookies as Playwright state
- `cookie-sync/hermes-browser-sync.config.json` — Hermes-side integration template
- `telegram-toolkit/` — Telegram CLI, bot interaction, music bot
- `research/` — platform research scripts
- `skills/` — Hermes skills and references

## Security rules

- Never commit real cookies, tokens, `.env`, or session files
- Keep the backend behind HTTPS or a tunnel
- Use placeholders in examples only

## If you are installing on a fresh Hermes instance

1. Read the [Installation Guide](installation.md)
2. Install Hermes skills from `skills/`
3. Install research scripts from `research/scripts/`
4. Build the client extension from `cookie-sync/client/`
5. Run the backend from `cookie-sync/backend/`
6. Configure domains and API keys
7. Verify with `agent-reach doctor --json`

## Troubleshooting

- If the browser extension cannot reach the backend, use Cloudflare Tunnel or another HTTPS proxy.
- If Telegram login fails, delete `telegram-toolkit/telegram.session` and log in again.
- If a research backend is unavailable, run `agent-reach doctor --json` and install the missing channel.

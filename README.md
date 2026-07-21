# Hermes Agent Toolkit

> Complete AI-agent toolkit for cookie sync, Telegram automation, and multi-platform research.  
> Built on top of [Agent-Reach](https://github.com/Panniantong/Agent-Reach), the mother project.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-green.svg)](https://developer.chrome.com/docs/extensions/)

---

## What this project is

Hermes Agent Toolkit is a bundled package of:

1. **Cookie Sync** — a two-part system for syncing authenticated browser cookies from a user’s machine to a Hermes backend.
2. **Telegram Toolkit** — Telethon-based CLI tools for Telegram search, download, export, monitoring, and bot interaction.
3. **Research Tools** — Agent-Reach-based scripts and skills for searching and reading across 16+ platforms.
4. **Hermes Skills** — packaged skills that let a fresh Hermes instance use the toolkit immediately.

This repository is designed so a user can:
- install a browser extension on their own machine,
- run a backend on Hermes or any server they control,
- connect the two with a secure API key,
- and use the synced session state in Playwright-based automation.

---

## What’s included

### 1) Cookie Sync
Two-part cookie sync system:

| Component | Path | Description |
|-----------|------|-------------|
| Client extension | `cookie-sync/client/` | CacheCat-based Chrome extension installed on the user's machine |
| Hermes backend | `cookie-sync/backend/` | FastAPI webhook server that receives cookies and writes Playwright `storage_state.json` |
| Hermes integration config | `cookie-sync/hermes-browser-sync.config.json` | Template file that tells Hermes where to read synced storage state |

### 2) Telegram Toolkit
Full Telegram automation:

| Feature | Description |
|---------|-------------|
| Search | Search messages in channels |
| Download | Download media (photos, videos, audio) |
| Export | Export messages to JSON/CSV |
| Monitor | Real-time channel monitoring |
| Bot interaction | Click buttons in any bot |
| Music bot | Interact with `@whatsmusicbot` |

### 3) Research Tools
Token-compressed research toolkit for 16+ platforms:

| Platform | Features |
|----------|----------|
| Web | Jina Reader, full-text search |
| Twitter/X | Search, timeline, user info |
| YouTube | Search, download, subtitles |
| Reddit | Search, posts, comments |
| TikTok | Search, video info |
| Bilibili | Search, video info, subtitles |
| Telegram | Search, download, monitor |
| Grok | AI-powered search |
| Multi-platform | Auto-update all tools |

### 4) Hermes Skills
Skills included for direct Hermes installation:

| Skill | Description |
|-------|-------------|
| `agent-reach` | Main skill — 16 platforms, multi-backend routing |
| `deep-research` | Deep research with delegation |
| `research-manager` | Research orchestration |
| `web-research` | Web research with multiple sources |
| `deep-research-optimized` | Token-optimized deep research |
| `telegram-music-bot` | Music bot interaction |

---

## Documentation

### English
- [Installation Guide](docs/installation.md)
- [Main Docs](docs/README.en.md)
- [Cookie Sync Overview](cookie-sync/README.md)
- [Cookie Sync Client](cookie-sync/client/README.md)
- [Cookie Sync Backend](cookie-sync/backend/README.md)
- [Telegram Toolkit](telegram-toolkit/README.md)
- [Research Tools](research/README.md)

### فارسی
- [راهنمای نصب](docs/installation.fa.md)
- [مستندات اصلی](docs/README.fa.md)
- [نمای کلی Cookie Sync](cookie-sync/README.md)
- [راهنمای کلاینت Cookie Sync](cookie-sync/client/README.fa.md)
- [راهنمای بک‌اند Cookie Sync](cookie-sync/backend/README.fa.md)
- [ابزارهای تلگرام](telegram-toolkit/README.md)
- [ابزارهای ریسرچ](research/README.md)

---

## Quick start

For full installation instructions, see [docs/installation.md](docs/installation.md).

### Minimal setup

```bash
git clone https://github.com/Amirezamky9/hermes-agent-toolkit.git
cd hermes-agent-toolkit
pip install -r requirements.txt
```

### Install Hermes skills

```bash
cp -r skills/* ~/.hermes/skills/
cp research/scripts/*.sh ~/.hermes/scripts/
chmod +x ~/.hermes/scripts/*.sh
```

---

## Cookie Sync workflow

### Client side
1. Build the extension from `cookie-sync/client/`
2. Load `cookie-sync/client/dist/` in Chrome
3. Open the extension dashboard
4. Configure domains to sync
5. Enable `Hermes Sync`

### Hermes backend side
1. Run `cookie-sync/backend/main.py` on your Hermes server
2. Set `HERMES_API_KEY`
3. Point the extension to the backend URL
4. Optional: use Cloudflare Tunnel if the backend is not publicly reachable

### Hermes integration
1. Place `cookie-sync/hermes-browser-sync.config.json` in the Hermes project root
2. Point it to your backend URL
3. Hermes reads the synced `storage_state.json` for authenticated browser sessions

---

## Main directories

```text
hermes-toolkit/
├── cookie-sync/
│   ├── client/              # CacheCat-based browser extension
│   ├── backend/             # FastAPI webhook server
│   ├── hermes-browser-sync.config.json
│   └── README.md
├── telegram-toolkit/
├── research/
├── skills/
├── docs/
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Credits and thanks

This project is built on top of these open-source projects:

| Project | Role |
|---------|------|
| [Agent-Reach](https://github.com/Panniantong/Agent-Reach) | Mother project for research routing |
| [CacheCat](https://github.com/chinmay29hub/CacheCat) | Chrome extension base for cookie sync |
| [Telethon](https://github.com/LonamiWebs/Telethon) | Telegram MTProto client |
| [telegram_media_downloader](https://github.com/Dineshkarthik/telegram_media_downloader) | Bulk media download |
| [TelegramTools](https://github.com/DilshanHarshajith/TelegramTools) | Modular Telegram scraping |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Video extraction |
| [Exa](https://exa.ai) | Web search |
| [Jina Reader](https://github.com/jina-ai/reader) | Web reading |
| [GitHub CLI](https://github.com/cli/cli) | GitHub operations |

---

## Security notes

- Never commit real cookies, session files, API keys, or tokens
- Use `.env.example` files as templates only
- Keep Hermes backend behind HTTPS or a tunnel
- Use separate browser profiles for testing when possible

## License

MIT License. See [LICENSE](LICENSE).

# Hermes Agent Toolkit

> Complete AI-agent toolkit for cookie sync, Telegram automation, and multi-platform research.
> Built on top of [Agent-Reach](https://github.com/Panniantong/Agent-Reach), the mother project.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-green.svg)](https://developer.chrome.com/docs/extensions/)

---

## Table of contents

- [What this project is](#what-this-project-is)
- [What’s included](#whats-included)
- [How the pieces fit together](#how-the-pieces-fit-together)
- [Repository layout](#repository-layout)
- [Quick start](#quick-start)
- [Installation](#installation)
- [Cookie Sync: client + backend](#cookie-sync-client--backend)
- [Telegram Toolkit](#telegram-toolkit)
- [Research Tools](#research-tools)
- [Hermes Skills](#hermes-skills)
- [Hermes integration](#hermes-integration)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)
- [Documentation in Persian](#documentation-in-persian)
- [License](#license)

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

| Component | Path | Description |
|-----------|------|-------------|
| Client extension | `cookie-sync/client/` | CacheCat-based Chrome extension installed on the user’s machine |
| Hermes backend | `cookie-sync/backend/` | FastAPI webhook server that receives cookies and writes Playwright `storage_state.json` |
| Hermes config template | `cookie-sync/hermes-browser-sync.config.json` | Template file that tells Hermes where to read synced storage state |

### 2) Telegram Toolkit

| Feature | Description |
|---------|-------------|
| Search | Search messages in channels or globally |
| Download | Download media from channels |
| Export | Export messages to JSON/CSV |
| Monitor | Real-time channel monitoring |
| Bot interaction | Click inline buttons in bots |
| Music bot | Search and download music via `@whatsmusicbot` |

### 3) Research Tools

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

| Skill | Description |
|-------|-------------|
| `agent-reach` | Main skill — 16 platforms, multi-backend routing |
| `deep-research` | Deep research with delegation |
| `research-manager` | Research orchestration |
| `web-research` | Web research with multiple sources |
| `deep-research-optimized` | Token-optimized deep research |
| `telegram-music-bot` | Music bot interaction |

---

## How the pieces fit together

```text
User machine
└── Chrome + Cookie Sync Client (CacheCat extension)
    └── Captures cookies for configured domains
    └── Sends them to the Hermes backend

Hermes / server side
└── Cookie Sync Backend (FastAPI)
    └── Receives cookies via webhook
    └── Writes Playwright storage_state.json
    └── Hermes / Playwright / automation jobs reuse authenticated sessions

Hermes agent side
├── Telegram Toolkit
├── Research Tools
└── Hermes Skills
```

---

## Repository layout

```text
hermes-agent-toolkit/
├── cookie-sync/
│   ├── client/               # Chrome extension source + dist build
│   ├── backend/              # FastAPI webhook backend
│   ├── hermes-browser-sync.config.json
│   └── README.md
├── telegram-toolkit/         # Telegram CLI + bot tools
├── research/                 # Agent-Reach research scripts
├── skills/                   # Hermes skills and references
├── docs/                     # English + Persian docs
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Quick start

If you want the full, step-by-step install instructions, read:

- [English installation guide](docs/installation.md)
- [Persian installation guide](docs/installation.fa.md)

Minimal setup:

```bash
git clone https://github.com/Amirezamky9/hermes-agent-toolkit.git
cd hermes-agent-toolkit
pip install -r requirements.txt
```

Install Hermes skills and scripts:

```bash
cp -r skills/* ~/.hermes/skills/
cp research/scripts/*.sh ~/.hermes/scripts/
chmod +x ~/.hermes/scripts/*.sh
```

---

## Installation

### Prerequisites

#### On the Hermes machine
- Python 3.10+
- Node.js 18+
- Git
- `pipx` recommended
- `gh` CLI for GitHub operations
- `mcporter` for Exa search integration

#### On the user machine
- Google Chrome 88+
- Permission to install Chrome extensions
- A browser profile that is already logged in to the target websites, if you want to sync cookies

### Install the repo

```bash
git clone https://github.com/Amirezamky9/hermes-agent-toolkit.git
cd hermes-agent-toolkit
pip install -r requirements.txt
```

### Install Hermes skills

```bash
cp -r skills/* ~/.hermes/skills/
chmod -R u+rwX ~/.hermes/skills
```

### Install research scripts

```bash
cp research/scripts/*.sh ~/.hermes/scripts/
chmod +x ~/.hermes/scripts/*.sh
```

### Configure Agent-Reach

If Agent-Reach is not already installed on the Hermes machine:

```bash
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto
agent-reach doctor --json
```

Agent-Reach provides access to many research channels, including:
- Web search via Jina / Exa
- Twitter/X
- Reddit
- YouTube
- GitHub
- Bilibili
- Telegram
- RSS
- V2EX
- Facebook
- Instagram
- LinkedIn
- XiaoHongShu
- Xueqiu
- Grok

If a backend is shown as `warn` or `off`, follow the `agent-reach doctor --json` output and install the missing channel.

---

## Cookie Sync: client + backend

The cookie sync system has **two separate parts**:

### A. Client extension (`cookie-sync/client/`)
This is the Chrome extension the user installs on their own computer.

It:
- captures cookies for selected domains,
- sends them to the backend,
- supports manual sync and optional auto-sync,
- never logs cookie values to the console.

### B. Hermes backend (`cookie-sync/backend/`)
This is the FastAPI service that runs on Hermes or another server you control.

It:
- receives cookie payloads,
- merges them into Playwright `storage_state.json`,
- exposes `/api/browser-sync`, `/api/test-connection`, and `/health`,
- can be placed behind Cloudflare Tunnel or any HTTPS reverse proxy.

### C. Hermes integration config
The file `cookie-sync/hermes-browser-sync.config.json` is a template that describes:
- the webhook endpoint,
- the payload format,
- the Playwright storage state path Hermes should use.

### Cookie sync flow

```text
Chrome extension -> webhook backend -> storage_state.json -> Playwright session
```

### Client setup

```bash
cd cookie-sync/client
npm install
npm run build
```

Build output:

```text
cookie-sync/client/dist/
```

Load into Chrome:
1. Open `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked**
4. Select `cookie-sync/client/dist/`

Then in the extension dashboard:
- open **Hermes Sync**,
- enable sync,
- enter backend URL,
- enter API key,
- add domains to sync.

Example domains:
- `google.com`
- `notebooklm.google.com`
- `x.com`

### Backend setup

```bash
cd cookie-sync/backend
cp .env.example .env
pip install -r requirements.txt
python main.py
```

Environment variables:
- `HERMES_API_KEY`
- `STORAGE_STATE_PATH`
- `BACKEND_HOST`
- `BACKEND_PORT`

### Cloudflare / remote access fallback
If the backend is not directly reachable from the user’s machine, run it behind Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
```

Then point the extension to the tunnel URL, for example:

```text
https://your-tunnel.trycloudflare.com/api/browser-sync
```

### Hermes-side integration
1. Copy `cookie-sync/hermes-browser-sync.config.json` into the Hermes project root.
2. Point it to the backend URL.
3. Make Hermes use the resulting `storage_state.json` in Playwright.

Example:

```python
context = browser.new_context(storage_state="storage_state.json")
```

---

## Telegram Toolkit

The Telegram toolkit lives in:

```text
telegram-toolkit/
```

It provides:
- `cli.py` for search / download / export / info / monitor
- `music_bot.py` for music search and download
- `bot_interactor.py` for clicking inline keyboard buttons
- `auto_join.py` for bots that require channel subscriptions

### Configure Telegram

1. Go to https://my.telegram.org/apps
2. Create an app
3. Copy your `api_id` and `api_hash`
4. Put them into `telegram-toolkit/config.yaml`

```bash
cd telegram-toolkit
cp config.yaml.example config.yaml
python3 cli.py info @telegram
```

The first run will prompt for your phone number and verification code.

### Telegram examples

```bash
python3 cli.py search "query" --channel @channel
python3 cli.py download @channel --limit 100
python3 cli.py export @channel --format json
python3 cli.py monitor @channel
python3 music_bot.py search "Hello Adele"
python3 music_bot.py full "Hello Adele" --output /tmp/
```

---

## Research Tools

The research toolkit lives in:

```text
research/
```

It includes token-compressed wrappers for:
- web search
- Twitter/X
- YouTube
- Reddit
- TikTok
- Bilibili
- Telegram
- Grok
- auto-update for the whole stack

### Main scripts

```bash
./research/scripts/research-web.sh "AI agent"
./research/scripts/research-twitter.sh "machine learning"
./research/scripts/research-youtube.sh "python tutorial"
./research/scripts/research-reddit.sh "deep learning"
./research/scripts/research-tiktok.sh "coding"
./research/scripts/research-bilibili.sh "anime"
./research/scripts/research-telegram.sh "AI" "@channel"
./research/scripts/research-grok.sh "query"
./research/scripts/agent-reach-update.sh
```

### Notes
- Each script already applies rate limits and output compression.
- Use these scripts instead of raw API responses when you want a shorter context.
- For fresh state, run `agent-reach doctor --json`.

---

## Hermes Skills

Copy the bundled skills into your Hermes instance:

```bash
cp -r skills/* ~/.hermes/skills/
```

### Included skills
- `agent-reach`
- `deep-research`
- `research-manager`
- `web-research`
- `deep-research-optimized`
- `telegram-music-bot`

### What `agent-reach` does
Agent-Reach is the mother project that routes many platforms and backends:
- Twitter/X
- Reddit
- YouTube
- GitHub
- Bilibili
- Telegram
- RSS
- V2EX
- Facebook
- Instagram
- LinkedIn
- XiaoHongShu
- Xueqiu
- Web search / Jina
- Exa
- Grok

---

## Documentation in Persian

If you prefer Persian, read:
- [راهنمای نصب](docs/installation.fa.md)
- [مستندات اصلی](docs/README.fa.md)
- [راهنمای کلاینت Cookie Sync](cookie-sync/client/README.fa.md)
- [راهنمای بک‌اند Cookie Sync](cookie-sync/backend/README.fa.md)

---

## Security

- Never commit real cookies, session files, API keys, tokens, or `.env` files
- Use the provided `.env.example` files only as templates
- Keep the backend behind HTTPS, a trusted proxy, or Cloudflare Tunnel
- Prefer a separate browser profile for testing cookie sync
- Use placeholders in docs and examples only

---

## Troubleshooting

### Cookie Sync does not connect
- Check the backend is running
- Check the extension API URL
- Check the API key on both sides
- If the backend is not reachable directly, use Cloudflare Tunnel

### Telegram login fails
- Delete `telegram-toolkit/telegram.session`
- Run `python3 cli.py info @telegram` again

### Research backend is unavailable
- Run `agent-reach doctor --json`
- Install the missing backend or login method

### Build fails for the Chrome extension
- Ensure Node.js 18+ is installed
- Re-run `npm install`
- Build output should be in `cookie-sync/client/dist/`

---

## Credits

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

## License

MIT License. See [LICENSE](LICENSE).

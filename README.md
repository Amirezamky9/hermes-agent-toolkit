# 🛠️ Hermes Toolkit

> Complete AI agent toolkit — cookie sync, Telegram automation, and research tools for 16+ platforms.
> Built on top of [Agent-Reach](https://github.com/Panniantong/Agent-Reach), the mother project.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 📦 What's Included

### 1. Cookie Sync
Sync browser cookies to server tools automatically.

| Component | Description |
|-----------|-------------|
| **CacheCat** | Chrome extension for cookie management |
| **Webhook Server** | Python server receiving cookies |

### 2. Telegram Toolkit
Full-featured Telegram automation.

| Feature | Description |
|---------|-------------|
| **Search** | Search messages in channels |
| **Download** | Download media (photos, videos, audio) |
| **Export** | Export messages to JSON/CSV |
| **Monitor** | Real-time channel monitoring |
| **Music Bot** | Interact with @whatsmusicbot |
| **Bot Interactor** | Click buttons in any bot |

### 3. Research Tools
Complete research toolkit for AI agents — search, download, and monitor across 16+ platforms.

| Platform | Features |
|----------|----------|
| **Web** | Jina Reader, full-text search |
| **Twitter/X** | Search, timeline, user info |
| **YouTube** | Search, download, subtitles |
| **Reddit** | Search, posts, comments |
| **TikTok** | Search, video info |
| **Bilibili** | Search, video info, subtitles |
| **Telegram** | Search, download, monitor |
| **Grok** | AI-powered search |
| **Multi-platform** | Auto-update all tools |

### 4. Skills (for Hermes)

| Skill | Description |
|-------|-------------|
| **agent-reach** | Main skill — 16 platforms, multi-backend routing |
| **deep-research** | Deep research with delegation |
| **research-manager** | Research orchestration |
| **web-research** | Web research with multiple sources |
| **deep-research-optimized** | Token-optimized deep research |
| **telegram-music-bot** | Music bot interaction |

## 🚀 Quick Start

**For complete installation guide, see [docs/installation.md](docs/installation.md)**

### Prerequisites

- Python 3.10+
- Google Chrome (for CacheCat)
- Telegram account

### Installation

```bash
# Clone repository
git clone https://github.com/Amirezamky9/hermes-toolkit.git
cd hermes-toolkit

# Install dependencies
pip install -r requirements.txt
```

### Cookie Sync Setup

#### Step 1: Install CacheCat Extension

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode"
4. Click "Load unpacked"
5. Select `cookie-sync/cachecat-extension/` folder

#### Step 2: Start Webhook Server

```bash
# Generate a secure token
export COOKIE_SYNC_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Start server
python3 cookie-sync/webhook.py
```

#### Step 3: Configure Extension

1. Click CacheCat icon in Chrome toolbar
2. Enter webhook URL: `http://localhost:9999`
3. Enter your token
4. Click "Sync" on any website

### Telegram Toolkit Setup

#### Step 1: Get API Keys

1. Go to https://my.telegram.org/apps
2. Create an application
3. Copy `api_id` and `api_hash`

#### Step 2: Configure

```bash
# Create config
cat > telegram-toolkit/config.yaml << EOF
api_id: YOUR_API_ID
api_hash: YOUR_API_HASH
EOF
```

#### Step 3: Login

```bash
cd telegram-toolkit
python3 cli.py info @telegram
# Enter phone number and code when prompted
```

## 📖 Usage

### Cookie Sync

```bash
# Start server
python3 cookie-sync/webhook.py

# Check health
curl http://localhost:9999/health
```

### Telegram Toolkit

```bash
cd telegram-toolkit

# Search messages
python3 cli.py search "query" --channel @channel

# Download media
python3 cli.py download @channel --limit 100

# Export to JSON
python3 cli.py export @channel --format json

# Monitor channel
python3 cli.py monitor @channel

# Get channel info
python3 cli.py info @channel
```

### Music Bot

```bash
cd telegram-toolkit

# Search for music
python3 music_bot.py search "Hello Adele"

# Download music
python3 music_bot.py download "Hello Adele"

# Full flow (search + download + lyrics)
python3 music_bot.py full "Hello Adele" --output /tmp/
```

### Research Tools

```bash
cd research

# Search web
./scripts/research-web.sh "AI agent"

# Search Twitter
./scripts/research-twitter.sh "machine learning"

# Search YouTube
./scripts/research-youtube.sh "python tutorial"

# Search Reddit
./scripts/research-reddit.sh "deep learning"

# Search TikTok
./scripts/research-tiktok.sh "coding"

# Search Bilibili
./scripts/research-bilibili.sh "anime"

# Search Telegram
./scripts/research-telegram.sh "AI" "@channel"

# Download from Telegram
./scripts/telegram-media-downloader.sh "@channel" 100

# Monitor Telegram channel
./scripts/telegram-channel-monitor.sh "@channel" 30

# Update all tools
./scripts/agent-reach-update.sh
```

## 🏗️ Architecture

```
hermes-toolkit/
├── cookie-sync/
│   ├── webhook.py              # Webhook server
│   ├── cachecat-extension/     # Chrome extension
│   └── README.md
├── telegram-toolkit/
│   ├── cli.py                  # Main CLI
│   ├── music_bot.py            # Music bot integration
│   ├── bot_interactor.py       # Bot button clicker
│   ├── modules/                # Additional modules
│   └── README.md
├── research/
│   ├── scripts/                # Research scripts
│   │   ├── research-web.sh
│   │   ├── research-twitter.sh
│   │   ├── research-youtube.sh
│   │   ├── research-reddit.sh
│   │   ├── research-tiktok.sh
│   │   ├── research-bilibili.sh
│   │   ├── research-telegram.sh
│   │   ├── research-grok.sh
│   │   ├── agent-reach-update.sh
│   │   ├── telegram-media-downloader.sh
│   │   └── telegram-channel-monitor.sh
│   └── README.md
├── skills/
│   ├── agent-reach/            # Main skill (16 platforms)
│   │   ├── SKILL.md
│   │   ├── references/         # 20 reference docs
│   │   └── scripts/            # Helper scripts
│   ├── research/               # Research skills
│   │   ├── deep-research/
│   │   ├── research-manager/
│   │   └── web-research/
│   ├── deep-research-optimized/
│   └── telegram/
│       └── telegram-music-bot/
├── docs/
│   ├── installation.md         # Complete install guide
│   ├── cookie-sync.md
│   ├── telegram-toolkit.md
│   └── troubleshooting.md
├── requirements.txt
├── LICENSE
└── README.md
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COOKIE_SYNC_TOKEN` | Webhook auth token | Required |
| `COOKIE_SYNC_PORT` | Webhook port | 9999 |
| `TG_API_ID` | Telegram API ID | Required |
| `TG_API_HASH` | Telegram API Hash | Required |

### Config Files

| File | Purpose |
|------|---------|
| `telegram-toolkit/config.yaml` | Telegram settings |
| `~/.agent-reach/cookies/` | Cookie storage |

## 🛡️ Security

- Never commit `.env` or config files with credentials
- Use environment variables for sensitive data
- Rotate tokens regularly
- Use HTTPS in production

## 🐛 Troubleshooting

### Cookie Sync

```bash
# Server won't start
export COOKIE_SYNC_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
python3 cookie-sync/webhook.py

# Extension can't connect
# Check: Is server running? Is token correct?
curl http://localhost:9999/health
```

### Telegram Toolkit

```bash
# Login fails
# Delete session and retry
rm -f telegram-toolkit/telegram.session
python3 telegram-toolkit/cli.py info @telegram

# FloodWait error
# Wait for the specified time, script auto-handles

# Bot timeout
# Increase timeout in music_bot.py
```

## 📚 Credits & Acknowledgments

This project would not be possible without these amazing open-source projects and their developers.

### Core Dependencies

| Project | Author | Repository | Used For |
|---------|--------|------------|----------|
| **Agent-Reach** | Panniantong | [github.com/Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | Platform router for 16 platforms — Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu, LinkedIn, Facebook, Instagram, V2EX, Xueqiu, RSS, Telegram, Web, Exa Search, Grok |
| **CacheCat** | chinmay29hub | [github.com/chinmay29hub/CacheCat](https://github.com/chinmay29hub/CacheCat) | Chrome cookie extension |
| **Telethon** | LonamiWebs | [github.com/LonamiWebs/Telethon](https://github.com/LonamiWebs/Telethon) | Telegram MTProto client |
| **telegram_media_downloader** | Dineshkarthik | [github.com/Dineshkarthik/telegram_media_downloader](https://github.com/Dineshkarthik/telegram_media_downloader) | Bulk media download (2672⭐) |
| **TelegramTools** | DilshanHarshajith | [github.com/DilshanHarshajith/TelegramTools](https://github.com/DilshanHarshajith/TelegramTools) | Modular scraping |

### Research Tools (from Agent-Reach)

| Project | Author | Repository | Used For |
|---------|--------|------------|----------|
| **yt-dlp** | yt-dlp-org | [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube/video download (1752 extractors) |
| **Exa Search** | exa-labs | [exa.ai](https://exa.ai) | AI-powered web search |
| **Jina Reader** | jina-ai | [github.com/jina-ai/reader](https://github.com/jina-ai/reader) | Web page reading |
| **GitHub CLI** | cli | [github.com/cli/cli](https://github.com/cli/cli) | GitHub operations |
| **twitter-cli** | - | npm | Twitter/X operations |
| **rdt-cli** | - | npm | Reddit operations |
| **bili-cli** | - | npm | Bilibili operations |
| **mcporter** | - | npm | MCP tool integration |

### Special Thanks

- **Agent-Reach** — The mother project: platform router for 16 platforms with multi-backend routing, health checking, auto-update, and token-optimized research scripts. This project provides the foundation for all research capabilities.
- **CacheCat** — Chrome extension architecture that inspired our cookie-sync system
- **Telethon** — Excellent Telegram MTProto implementation
- **yt-dlp** — Comprehensive video platform support across 1752 extractors
- **Exa & Jina** — Powerful AI search and web reading capabilities
- **telegram_media_downloader** — Battle-tested bulk download with rate limiting (2672⭐)
- **TelegramTools** — Modular scraping, user export, and origin tracing

### License

All original code in this repository is MIT Licensed.
Individual dependencies retain their original licenses.

# Hermes Toolkit — Complete Package

## Repository

https://github.com/Amirezamky9/hermes-toolkit

## What It Is

Complete AI agent toolkit — cookie sync, Telegram automation, and research tools for 16+ platforms.
Built on top of Agent-Reach, the mother project.

## Structure (80 files, 25 directories)

```
hermes-toolkit/
├── cookie-sync/              # CacheCat-based browser cookie sync
│   ├── webhook.py            # HTTP server receiving cookies
│   ├── .env.example          # Config template
│   └── README.md
├── telegram-toolkit/         # Telethon-based Telegram automation
│   ├── cli.py                # Unified CLI (search/download/export/monitor/info)
│   ├── music_bot.py          # @whatsmusicbot integration
│   ├── bot_interactor.py     # Click buttons in any bot
│   ├── auto_join.py          # Auto-join required channels
│   ├── modules/              # 7 modules from TelegramTools
│   └── config.yaml.example
├── research/                 # Research scripts for 16+ platforms
│   ├── scripts/              # 11 token-optimized scripts
│   │   ├── research-web.sh       # Jina + Exa
│   │   ├── research-twitter.sh   # twitter-cli
│   │   ├── research-youtube.sh   # yt-dlp
│   │   ├── research-reddit.sh    # rdt-cli
│   │   ├── research-tiktok.sh
│   │   ├── research-bilibili.sh  # bili-cli
│   │   ├── research-telegram.sh  # Telethon
│   │   ├── research-grok.sh      # xAI API
│   │   ├── agent-reach-update.sh # Auto-update all CLIs
│   │   ├── telegram-media-downloader.sh
│   │   └── telegram-channel-monitor.sh
│   └── README.md
├── skills/                   # Hermes skills (copy to ~/.hermes/skills/)
│   ├── agent-reach/          # Main skill (16 platforms)
│   │   ├── SKILL.md
│   │   ├── references/       # 20 reference docs
│   │   └── scripts/          # 7 helper scripts
│   ├── research/             # Research skills
│   │   ├── deep-research/
│   │   ├── research-manager/
│   │   └── web-research/
│   ├── deep-research-optimized/
│   └── telegram/
│       └── telegram-music-bot/
├── docs/
│   ├── installation.md       # Complete install guide
│   ├── cookie-sync.md
│   ├── telegram-toolkit.md
│   └── troubleshooting.md
├── requirements.txt
├── LICENSE (MIT)
└── README.md
```

## Installation on New Hermes Instance

```bash
# 1. Clone
git clone https://github.com/Amirezamky9/hermes-toolkit.git
cd hermes-toolkit

# 2. Install Python deps
pip install -r requirements.txt

# 3. Install CLIs
pip install yt-dlp
pipx install twitter-cli
pipx install bilibili-cli
sudo apt install gh
npm install -g mcporter

# 4. Copy skills
cp -r skills/* ~/.hermes/skills/

# 5. Copy scripts
cp research/scripts/*.sh ~/.hermes/scripts/

# 6. Setup Telegram
cd telegram-toolkit
cp config.yaml.example config.yaml
nano config.yaml  # Add API keys
python3 cli.py info @telegram  # Login

# 7. Setup Exa
mcporter config add exa https://mcp.exa.ai/mcp

# 8. Verify
agent-reach doctor --json
```

## Credits (13 projects)

| Project | Author | Used For |
|---------|--------|----------|
| **Agent-Reach** | Panniantong | Platform router for 16 platforms |
| **CacheCat** | chinmay29hub | Chrome cookie extension |
| **Telethon** | LonamiWebs | Telegram MTProto |
| **telegram_media_downloader** | Dineshkarthik | Bulk download (2672⭐) |
| **TelegramTools** | DilshanHarshajith | Modular scraping |
| **yt-dlp** | yt-dlp-org | Video download (1752 extractors) |
| **Exa Search** | exa-labs | AI-powered search |
| **Jina Reader** | jina-ai | Web page reading |
| **GitHub CLI** | cli | GitHub operations |
| **twitter-cli** | npm | Twitter/X |
| **rdt-cli** | npm | Reddit |
| **bili-cli** | npm | Bilibili |
| **mcporter** | npm | MCP integration |

## Sensitive Data Excluded

- API keys (use .env.example / config.yaml.example)
- Session files (.session)
- Cookie files (.json)
- Tokens

## Build Pattern

1. Search GitHub for existing solutions
2. Fork/combine best projects (2672⭐ + modular scraping)
3. Add research tools from Agent-Reach
4. Copy skills and references
5. Sanitize (remove credentials)
6. Write comprehensive documentation
7. Add credits for all source projects
8. **Rebuild git history from scratch** (rm -rf .git → git init → single commit → force push)
9. Push to GitHub

## Bot Subscription Pattern

Many Telegram bots require joining channels before interaction. The pattern:

1. Send `/start` to bot
2. Check if reply contains subscription message (buttons with "مشترک" / "subscribe")
3. Join required channels via `JoinChannelRequest`
4. Click "check subscription" button (data: `check_unified_sub`)
5. Retry original action

Implementation: `auto_join.py` handles this automatically.
Pitfall: Bots may show search results but block download until subscription is verified.

## New support files

- `references/fainal-hermes-coki.md` — client-side CacheCat install package, server sync flow, and sensitive-data exclusion rules
- `references/cookie-sync-client-package.md` — packaging and publish checklist for the user-installed client side
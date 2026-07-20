# 🔍 Agent Research Tools

> Complete research toolkit for AI agents — search, download, and monitor across 16+ platforms.
> Built on top of [Agent-Reach](https://github.com/Panniantong/Agent-Reach), the mother project.

## What is Agent-Reach?

Agent-Reach is a **platform router** that provides unified access to 16 platforms with multiple backends:

| Platform | Backend | Features |
|----------|---------|----------|
| **Twitter/X** | twitter-cli, OpenCLI | Search, timeline, user info |
| **Reddit** | rdt-cli, OpenCLI | Search, posts, comments |
| **YouTube** | yt-dlp | Search, download, subtitles |
| **GitHub** | gh CLI | Repos, issues, PRs |
| **Bilibili** | bili-cli | Search, video info, subtitles |
| **XiaoHongShu** | OpenCLI | Search, posts, comments |
| **LinkedIn** | linkedin-scraper-mcp | Jobs, profiles |
| **Facebook** | OpenCLI | Search, groups, pages |
| **Instagram** | OpenCLI | Search, profiles, posts |
| **V2EX** | API | Hot topics, nodes |
| **Xueqiu** | API | Stocks, finance |
| **RSS** | feedparser | Feed reading |
| **Telegram** | Telethon | Search, download, monitor |
| **Web** | Jina Reader | Full-text reading |
| **Exa Search** | mcporter | AI-powered search |
| **Grok** | xAI API | AI-powered search |

## Supported Platforms

| Platform | Script | Features |
|----------|--------|----------|
| **Web** | `research-web.sh` | Jina Reader, full-text search |
| **Twitter/X** | `research-twitter.sh` | Search, timeline, user info |
| **YouTube** | `research-youtube.sh` | Search, download, subtitles |
| **Reddit** | `research-reddit.sh` | Search, posts, comments |
| **TikTok** | `research-tiktok.sh` | Search, video info |
| **Bilibili** | `research-bilibili.sh` | Search, video info, subtitles |
| **Telegram** | `research-telegram.sh` | Search, download, monitor |
| **Grok** | `research-grok.sh` | AI-powered search |
| **Multi-platform** | `agent-reach-update.sh` | Auto-update all tools |

## Tools Required

| Tool | Repository | Install |
|------|------------|---------|
| **Agent-Reach** | [github.com/Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | `pipx install agent-reach` |
| **yt-dlp** | [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | `pip install yt-dlp` |
| **Telethon** | [github.com/LonamiWebs/Telethon](https://github.com/LonamiWebs/Telethon) | `pip install telethon` |
| **Exa Search** | [exa.ai](https://exa.ai) | `mcporter config add exa` |
| **Jina Reader** | [github.com/jina-ai/reader](https://github.com/jina-ai/reader) | `curl` (always available) |
| **GitHub CLI** | [github.com/cli/cli](https://github.com/cli/cli) | `apt install gh` |
| **twitter-cli** | npm | `npm install -g twitter-cli` |
| **rdt-cli** | npm | `npm install -g rdt-cli` |
| **bili-cli** | npm | `npm install -g bili-cli` |
| **mcporter** | npm | `npm install -g mcporter` |

## Quick Start

### 1. Install Agent-Reach

```bash
# Install agent-reach
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip

# Setup channels
agent-reach install --env=auto

# Check health
agent-reach doctor --json
```

### 2. Install Dependencies

```bash
# Core tools
pip install telethon yt-dlp

# Research scripts
chmod +x research/scripts/*.sh
```

### 3. Set Environment Variables

```bash
# Required for some platforms
export TWITTER_AUTH_TOKEN="your_token"
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_secret"
export GROK_API_KEY="your_key"
```

### 4. Run Scripts

```bash
# Search web
./research/scripts/research-web.sh "AI agent"

# Search Twitter
./research/scripts/research-twitter.sh "machine learning"

# Search YouTube
./research/scripts/research-youtube.sh "python tutorial"

# Search Reddit
./research/scripts/research-reddit.sh "deep learning"

# Search TikTok
./research/scripts/research-tiktok.sh "coding"

# Search Bilibili
./research/scripts/research-bilibili.sh "anime"

# Search Telegram
./research/scripts/research-telegram.sh "AI" "@channel"

# Update all tools
./research/scripts/agent-reach-update.sh
```

## Usage Examples

### Web Search (Jina Reader + Exa)

```bash
# Basic search
./research/scripts/research-web.sh "AI agent frameworks"

# With limit
./research/scripts/research-web.sh "machine learning" 10
```

### Twitter Search (twitter-cli)

```bash
# Search tweets
./research/scripts/research-twitter.sh "openai"

# Search with limit
./research/scripts/research-twitter.sh "chatgpt" 20
```

### YouTube Search (yt-dlp)

```bash
# Search videos
./research/scripts/research-youtube.sh "python tutorial"

# Search with limit
./research/scripts/research-youtube.sh "machine learning" 10
```

### Reddit Search (rdt-cli)

```bash
# Search posts
./research/scripts/research-reddit.sh "deep learning"

# Search in specific subreddit
./research/scripts/research-reddit.sh "machine learning" 10 "r/MachineLearning"
```

### TikTok Search

```bash
# Search videos
./research/scripts/research-tiktok.sh "coding"

# Search with limit
./research/scripts/research-tiktok.sh "python" 5
```

### Bilibili Search (bili-cli)

```bash
# Search videos
./research/scripts/research-bilibili.sh "anime"

# Search with limit
./research/scripts/research-bilibili.sh "coding" 10
```

### Telegram Search (Telethon)

```bash
# Search globally
./research/scripts/research-telegram.sh "AI"

# Search in specific channel
./research/scripts/research-telegram.sh "update" "@channel"

# With limit
./research/scripts/research-telegram.sh "query" "@channel" 20
```

### Telegram Download (Telethon)

```bash
# Download media from channel
./research/scripts/telegram-media-downloader.sh "@channel" 100

# Download with type filter
./research/scripts/telegram-media-downloader.sh "@channel" 50 "photo"
```

### Telegram Monitor (Telethon)

```bash
# Monitor channel in real-time
./research/scripts/telegram-channel-monitor.sh "@channel" 30

# Monitor with custom interval
./research/scripts/telegram-channel-monitor.sh "@channel" 60
```

### Update All Tools (Agent-Reach)

```bash
# Update all CLIs
./research/scripts/agent-reach-update.sh

# Update specific tool
./research/scripts/agent-reach-update.sh yt-dlp
```

## Architecture

```
research/
├── scripts/
│   ├── research-web.sh           # Web search (Jina + Exa)
│   ├── research-twitter.sh       # Twitter/X search (twitter-cli)
│   ├── research-youtube.sh       # YouTube search (yt-dlp)
│   ├── research-reddit.sh        # Reddit search (rdt-cli)
│   ├── research-tiktok.sh        # TikTok search
│   ├── research-bilibili.sh      # Bilibili search (bili-cli)
│   ├── research-telegram.sh      # Telegram search (Telethon)
│   ├── research-grok.sh          # Grok AI search (xAI API)
│   ├── agent-reach-update.sh     # Update all tools
│   ├── telegram-media-downloader.sh  # Download media (Telethon)
│   └── telegram-channel-monitor.sh   # Monitor channel (Telethon)
└── README.md
```

## Rate Limits

| Platform | Limit | Delay |
|----------|-------|-------|
| Twitter/X | 2s | Auto |
| YouTube | 2s | Auto |
| Reddit | 1s | Auto |
| TikTok | 1s | Auto |
| Bilibili | 1s | Auto |
| Telegram | 2s | Auto |
| Exa | 1s | Auto |
| Jina | 1s | Auto |

## Output Format

All scripts output JSON for easy parsing:

```json
{
  "query": "AI agent",
  "platform": "web",
  "results": [
    {
      "title": "Result title",
      "url": "https://...",
      "snippet": "Description..."
    }
  ],
  "count": 10,
  "has_more": false
}
```

## Auto-Update

The `agent-reach-update.sh` script automatically updates all tools:

```bash
# Update everything
./research/scripts/agent-reach-update.sh

# Check versions
./research/scripts/agent-reach-update.sh --check
```

## Troubleshooting

### Script not found

```bash
# Make executable
chmod +x research/scripts/*.sh

# Check PATH
export PATH="$PWD/research/scripts:$PATH"
```

### Rate limit error

```bash
# Wait and retry
sleep 5
./research/scripts/research-twitter.sh "query"
```

### Authentication error

```bash
# Check environment variables
echo $TWITTER_AUTH_TOKEN
echo $REDDIT_CLIENT_ID
```

## Credits & Acknowledgments

This research toolkit is built on top of these amazing open-source projects:

### The Mother Project

| Project | Author | Repository | Description |
|---------|--------|------------|-------------|
| **Agent-Reach** | Panniantong | [github.com/Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | Platform router for 16 platforms with multi-backend routing, health checking, auto-update, and token-optimized research scripts. The foundation for all research capabilities. |

### Core Tools

| Project | Author | Repository | Used For |
|---------|--------|------------|----------|
| **yt-dlp** | yt-dlp-org | [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube/video download (1752 extractors) |
| **Telethon** | LonamiWebs | [github.com/LonamiWebs/Telethon](https://github.com/LonamiWebs/Telethon) | Telegram MTProto client |
| **Exa Search** | exa-labs | [exa.ai](https://exa.ai) | AI-powered web search |
| **Jina Reader** | jina-ai | [github.com/jina-ai/reader](https://github.com/jina-ai/reader) | Web page reading |
| **GitHub CLI** | cli | [github.com/cli/cli](https://github.com/cli/cli) | GitHub operations |

### Platform-Specific Tools

| Project | Repository | Used For |
|---------|------------|----------|
| **twitter-cli** | npm | Twitter/X operations |
| **rdt-cli** | npm | Reddit operations |
| **bili-cli** | npm | Bilibili operations |
| **mcporter** | npm | MCP tool integration |

### Special Thanks

- **Agent-Reach** — The mother project: platform router for 16 platforms with multi-backend routing, health checking, auto-update, and token-optimized research scripts. This project provides the foundation for all research capabilities.
- **yt-dlp** — Comprehensive video platform support across 1752 extractors
- **Telethon** — Excellent Telegram MTProto implementation
- **Exa & Jina** — Powerful AI search and web reading capabilities
- **CacheCat** — Chrome extension architecture (in cookie-sync module)

### License

All original code in this repository is MIT Licensed.
Individual dependencies retain their original licenses.

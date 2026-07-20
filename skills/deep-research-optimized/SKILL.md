---
name: deep-research-optimized
description: >-
  Token-optimized deep research skill. Uses pre-processing scripts to minimize
  LLM token usage. Includes rate limit protection, parallel execution, and
  multi-platform research via agent-reach tools.
version: 1.0.0
triggers:
  - research
  - deep research
  - investigate
  - analyze
  - compare
  - evaluate
  - research topic
  - find information
  - look up
  - search about
related_skills:
  - agent-reach
  - web-research
  - research-manager
platforms:
  - linux
required_commands:
  - bash
  - curl
  - python3
  - yt-dlp
  - twitter
  - rdt
  - gh
  - mcporter
  - bili
---

# Deep Research Optimized — Token-Efficient Research Engine

## Core Principle

**Every tool call must pre-process data BEFORE it enters the LLM context.**
Raw API output = wasted tokens. Compressed output = efficient research.

## Token Budget Rules

| Action | Max Tokens | Method |
|--------|-----------|--------|
| Search query | 200 | Use `research-web.sh` |
| Single page read | 500 | Use Jina + head -c |
| Tweet batch | 300 | Use `research-twitter.sh` |
| YouTube metadata | 200 | Use `research-youtube.sh` |
| Reddit post | 400 | Use `research-reddit.sh` |
| GitHub repo | 150 | Use `gh search` + grep |
| Telegram bot interaction | 100 | Use `bot_interactor.py --json` |
| Full research task | 2000 | Orchestrated batch |

## Rate Limit Protection

```bash
# Minimum delays between API calls
MIN_DELAY=2  # seconds between Twitter searches
MIN_DELAY=1  # seconds between Exa searches
MIN_DELAY=0  # seconds between Jina reads (no limit observed)

# Max consecutive calls before forced break
MAX_CONSECUTIVE=5
BREAK_DURATION=30  # seconds
```

## Research Workflow (Token-Optimized)

### Phase 1: Quick Scan (100-200 tokens)
```bash
# Web search only - no page reads
bash ~/.hermes/scripts/research-web.sh "QUERY" 3 2>&1 | head -30
```

### Phase 2: Platform-Specific (200-500 tokens)
```bash
# Twitter sentiment
bash ~/.hermes/scripts/research-twitter.sh "QUERY" 5 2>&1

# Reddit discussions
bash ~/.hermes/scripts/research-reddit.sh "QUERY" "" 5 2>&1

# YouTube videos
bash ~/.hermes/scripts/research-youtube.sh "QUERY" 3 2>&1

# GitHub repos
gh search repos "QUERY" --sort stars --limit 5 2>&1 | head -10
```

### Phase 3: Deep Read (500-1000 tokens)
```bash
# Read top 2 pages only (compressed)
URLS=$(mcporter call "exa.web_search_exa(query: \"QUERY\", numResults: 2)" 2>&1 | grep "^URL:" | sed 's/^URL: //' | head -2)
for url in $URLS; do
  curl -s "https://r.jina.ai/$url" -H "Accept: text/plain" --max-time 15 2>/dev/null | head -c 2000
done
```

### Phase 4: Synthesis (500-1000 tokens)
- Merge findings from Phase 1-3
- Remove duplicates
- Extract key facts only
- State confidence level

## Platform-Specific Commands

### Twitter/X (via twitter-cli)
```bash
# Env vars MUST be set
source ~/.agent-reach/cookies/twitter.env
export TWITTER_AUTH_TOKEN TWITTER_CT0

# Search (compressed)
twitter search "QUERY" -n 5 2>&1 | head -50

# User info
twitter user USERNAME 2>&1 | head -10

# Rate limit: ~2s between searches, max 5 consecutive
```

### Reddit (via rdt-cli)
```bash
# Search
rdt search "QUERY" --limit 5 2>&1 | head -50

# Read post (use POST_ID, not URL)
rdt read POST_ID -n 20 --compact 2>&1 | head -100

# Rate limit: ~1s between calls, no strict limit observed
```

### YouTube (via yt-dlp)
```bash
# Config MUST have cookies + challenge solver
cat ~/.config/yt-dlp/config
# Should contain:
# --js-runtimes node
# --cookies ~/.agent-reach/cookies/youtube-cookies.txt
# --remote-components ejs:github

# Video info (compressed)
yt-dlp --dump-json --skip-download "URL" 2>/dev/null | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(f'Title: {d[\"title\"]}')
print(f'Views: {d.get(\"view_count\",0):,}')
print(f'Duration: {d.get(\"duration_string\",\"?\")}')
"

# Subtitles
yt-dlp --write-sub --write-auto-sub --sub-lang en --skip-download \
  --sub-format vtt -o "/tmp/yt-%(id)s" "URL" 2>/dev/null

# Rate limit: No strict limit, but be gentle (2s between calls)
```

### GitHub (via gh CLI)
```bash
# Search repos
gh search repos "QUERY" --sort stars --limit 5

# Repo info
gh repo view OWNER/REPO

# Rate limit: 1000 requests/hour authenticated
```

### Bilibili (via bili-cli)
```bash
# Search
bili search "QUERY" --type video -n 5

# Hot videos
bili hot -n 5

# Audio extraction (ASR-ready)
bili audio BV_ID

# Rate limit: No strict limit observed
```

### Web (via Exa + Jina)
```bash
# Semantic search
mcporter call 'exa.web_search_exa(query: "QUERY", numResults: 5)'

# Read page (compressed)
curl -s "https://r.jina.ai/URL" -H "Accept: text/plain" --max-time 15 | head -c 3000

# Rate limit: Exa ~1s, Jina no limit observed
```

### Telegram (via toolkit CLI)
```bash
# Search messages
cd ~/.agent-reach/tools/telegram-toolkit
python3 cli.py search "QUERY" --limit 5 --format ai

# Download media
python3 cli.py download @channel --limit 10 --type photo

# Export for analysis
python3 cli.py export @channel --format json --limit 50 --output /tmp/tg_export.json

# Bot interaction (click inline buttons)
python3 bot_interactor.py @botname --message "/start" --json

# Rate limit: 25 msg/sec safe, 5 downloads/sec safe
# Requires: TG_API_ID + TG_API_HASH in telegram.env
# ⚠️ First-time login uses two-step pattern (see agent-reach references/telegram-telethon.md)
#    client.start() fails in non-interactive sessions — use send_code_request() + sign_in()
# ⚠️ Bot import pitfall: use ReplyInlineMarkup, NOT InlineKeyboardMarkup
```

## Token Optimization Scripts

All scripts are in `~/.hermes/scripts/`:

| Script | Purpose | Token Savings |
|--------|---------|---------------|
| `research-web.sh` | Exa search + Jina read | 60% vs raw |
| `research-twitter.sh` | Twitter search + parse | 70% vs raw |
| `research-youtube.sh` | YouTube metadata + subs | 50% vs raw |
| `research-reddit.sh` | Reddit search | 40% vs raw |
| `research-tiktok.sh` | TikTok search + metadata | 50% vs raw |
| `research-bilibili.sh` | Bilibili search + hot | 50% vs raw |
| `research-grok.sh` | xAI API or Grok tweet fallback | 60% vs raw |
| `telegram-toolkit/cli.py` | Telegram search/download/monitor/export | 50% vs raw |
| `telegram-toolkit/bot_interactor.py` | Telegram bot interaction (inline buttons) | 60% vs raw |

## Parallel Execution Rules

```bash
# Safe to run in parallel (no rate limit conflicts):
# - Exa search + Jina read
# - GitHub search + Bilibili search
# - YouTube metadata + Reddit search
# - Telegram search + Twitter search

# MUST serialize (rate limit sensitive):
# - Twitter searches (2s delay between)
# - rdt searches (1s delay between)
# - Multiple Exa searches (1s delay between)
```

## Output Format

Research results MUST follow this structure:

```
## Research: [Topic]

### Sources Checked
- [Platform]: [count] results
- [Platform]: [count] results

### Key Findings
1. [Finding 1] (confidence: high/medium/low)
2. [Finding 2] (confidence: high/medium/low)

### Evidence
- [Source 1]: [key quote/fact]
- [Source 2]: [key quote/fact]

### Unknowns
- [What we couldn't verify]

### Recommendation
[Actionable conclusion]
```

## Cost Tracking

Before starting research, estimate:
- Number of platforms to check: N
- Expected API calls: N × 2-3
- Expected tokens: N × 300-500
- Total budget: Keep under 2000 tokens per research task

## AI Agent Token Optimization (Tool Design Principles)

When designing research tool schemas for AI agents:

### Schema Design
- Tool name: 3-5 tokens. Description: 10-20 tokens.
- Parameters: flat (not nested), typed, minimal.
- Use enums for categorical values (reduces hallucination).
- Optional params with sensible defaults (model omits when default suffices).
- Total schema budget: 60-90 tokens per 3-param tool. Max 150.

### Output Design
- Return ONLY what the model needs for the task.
- No decorative fields, no raw API dumps.
- Compressed text > JSON for readability.
- Use consistent structure across all tools.

### Parameter Design
- Flat parameters over nested objects.
- `{"query": "x", "limit": 5}` NOT `{"filters": {"query": "x"}, "pagination": {"limit": 5}}`.
- Every field in tool call output = tokens in conversation history.

## Pitfalls

### Intent Disambiguation (Persian/Arabic users)
When a Persian-speaking user asks about "اسکیل" (skill) in a Hermes context, it is ambiguous — they may mean either (a) Hermes Agent installable skills from the hub, or (b) general knowledge/career skills to learn. Always clarify before launching a full multi-platform research task. Use `clarify()` to disambiguate: "آیا منظورت اسکیل‌های Hermes هست یا مهارت‌های عمومی؟"

### Hermes Skills Hub Search
To search for installable Hermes skills (not web research), use the CLI directly:
```bash
/app/venv/bin/hermes skills search "QUERY"    # search hub
/app/venv/bin/hermes skills inspect ID        # preview before install
/app/venv/bin/hermes skills install ID        # install
```
Keywords that return cybersecurity results: security, pentest, vulnerability, hacking, osint, cve, threat, forensic, owasp, incident, malware, phishing, cyber, red team, blue team, nmap, exploit. Full catalog with identifiers: see `references/hermes-skills-hub-search.md`.

## When to Stop

Stop research when:
1. All key questions are answered with high confidence
2. Additional sources return duplicate information
3. Token budget is exhausted
4. Rate limits are hit

## Grok Integration

### Option A: xAI API (recommended)
```bash
# Requires XAI_API_KEY in ~/.agent-reach/cookies/xai.env
bash ~/.hermes/scripts/research-grok.sh "your question" grok-4
```

### Option B: Twitter search (public fallback)
```bash
# Find Grok's public responses on Twitter
twitter search "from:grok TOPIC" -n 3 2>&1 | head -30
```

**Limitation:** Twitter search only finds PUBLIC Grok responses, not custom queries.
For custom research, use the xAI API or Exa + Jina instead.

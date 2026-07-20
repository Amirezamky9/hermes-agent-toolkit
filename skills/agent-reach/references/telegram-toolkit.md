# Telegram Toolkit — Unified CLI Reference

## Architecture

Built from two GitHub projects merged into one CLI:

| Component | Source | Stars | Purpose |
|-----------|--------|-------|---------|
| media_downloader | Dineshkarthik/telegram_media_downloader | 2672 | Bulk download with rate limiting, resume, multi-chat |
| modules/* | DilshanHarshajith/TelegramTools | 1 | Modular scraping, user export, origin tracing |
| cli.py | custom | — | Unified CLI interface |
| ai/schema.py | custom | — | AI agent schemas (~92 tokens) |

Location: `~/.agent-reach/tools/telegram-toolkit/`

## First-time Setup

```bash
# 1. API keys must be in ~/.agent-reach/cookies/telegram.env
TG_API_ID=your_id
TG_API_HASH=your_hash

# 2. Login (one-time, requires phone + SMS code)
#    ⚠️ client.start() uses input() — fails in non-interactive sessions.
#    Use the two-step pattern from references/telegram-telethon.md:
cd ~/.agent-reach/tools/telegram-toolkit
python3 step1_send_code.py     # Sends code, saves phone_code_hash
# Enter SMS code when received → then:
echo "CODE" > .login_code
python3 step2_sign_in.py       # Signs in with code + hash
# Session saved to telegram.session

# 3. Verify
python3 cli.py info @telegram
```

## CLI Commands

### search — جستجوی پیام

```bash
python3 cli.py search "AI agent" --channel @channel_name --limit 10
python3 cli.py search "crypto" --limit 20 --format ai --output /tmp/results.json
```

Options:
- `--channel` / `-c`: @username or 'global' (default: global)
- `--limit` / `-l`: max results (default: 10)
- `--output` / `-o`: save JSON to file
- `--format` / `-f`: text or ai (ai = compact JSON for LLM)

### download — دانلود مدیا

```bash
python3 cli.py download @channel --limit 100
python3 cli.py download @channel --type video --delay 2
```

Options:
- `--limit` / `-l`: max files (default: 100)
- `--type` / `-t`: photo, video, all (default: all)
- `--output` / `-o`: output directory
- `--delay` / `-d`: seconds between downloads (default: 1.0)

### monitor — مانیتور زنده

```bash
python3 cli.py monitor @channel --interval 30
```

State saved to `monitor_@channel.json` for resume.

### export — خروجی گرفتن

```bash
python3 cli.py export @channel --format json --limit 1000
python3 cli.py export @channel --format csv --output ~/export.csv
```

### info — اطلاعات

```bash
python3 cli.py info @channel
python3 cli.py info @username
```

## AI Agent Schema

5 schemas, ~92 tokens total:

| Schema | Tokens | Purpose |
|--------|--------|---------|
| telegram_search | 21 | Search messages |
| telegram_download | 20 | Download media |
| telegram_monitor | 17 | Monitor channel |
| telegram_export | 20 | Export messages |
| telegram_info | 14 | Get info |

Schema definitions in `ai/schema.py`. Output schemas in `OUTPUT_SCHEMAS`.

## Rate Limits

| Operation | Hard limit | Toolkit safe zone |
|-----------|-----------|-------------------|
| Search req/sec | 30 | 25 |
| Download files | ~50 → FLOOD_WAIT | auto-retry with backoff |
| Send messages | 30/sec (userbot) | 25/sec |
| Join groups | 50/day | track carefully |

FloodWait handling: Telethon auto-sleeps for waits under `flood_sleep_threshold`
(default 60s). Longer waits are raised as exceptions.

## Config

`config.yaml` in toolkit dir:
```yaml
api_id: YOUR_API_ID_HERE
api_hash: your_hash
max_concurrent_downloads: 4
download_delay: 1.0
rate_limit:
  messages_per_sec: 25
  downloads_per_sec: 5
  flood_wait_threshold: 60
```

## Bot Interaction (bot_interactor.py)

Interact with Telegram bots that have inline keyboards (buttons).

```bash
cd ~/.agent-reach/tools/telegram-toolkit

# Simple: send message, get buttons
python3 bot_interactor.py @whatsmusicbot --message "/start" --json

# Interactive session (type numbers to click buttons)
python3 bot_interactor.py @whatsmusicbot --interactive
```

**Programmatic usage:**
```python
from bot_interactor import BotInteractor

bi = BotInteractor()
await bi.start()

# Send message, get reply with buttons
result = await bi.send_and_wait('@botname', '/start')
# result = {"text": "...", "buttons": [{"text": "...", "data": "...", "type": "inline"}], "message_id": 123}

# Click a button by data
result2 = await bi.click_button('@botname', result['message_id'], result['buttons'][0]['data'].encode())

# Click a button by text
result2 = await bi.click_button_by_text('@botname', result['message_id'], 'Button Text')

await bi.stop()
```

**Pitfall — Telethon types:** Inline keyboards use `ReplyInlineMarkup` + `KeyboardButtonCallback`, NOT `InlineKeyboardMarkup`. Import from `telethon.tl.types`.

**Pitfall — BotResponseTimeoutError:** Some bots timeout on `GetBotCallbackAnswerRequest`. The bot may require channel subscription first — see auto_join below.

## Auto-Join Subscription Channels (auto_join.py)

Many bots require joining channels before use. This script auto-detects and joins them.

```bash
python3 auto_join.py @whatsmusicbot
```

**Flow:**
1. Sends `/start` to bot
2. Detects subscription-required message (buttons with `t.me/` URLs)
3. Joins each channel via `JoinChannelRequest`
4. Clicks `check_unified_sub` button to verify

**Pitfall — subscription check:** After joining channels, you MUST click the "check subscriptions" button (`check_unified_sub` data). Without this, the bot still thinks you're not subscribed.

## File Structure

```
~/.agent-reach/tools/telegram-toolkit/
├── cli.py              # Unified CLI (search, download, monitor, export, info)
├── bot_interactor.py   # Bot interaction (inline keyboards, buttons)
├── auto_join.py        # Auto-join subscription channels for bots
├── login.py            # First-time login
├── config.yaml         # Configuration
├── telegram.session    # Session (auto-created on login)
├── README.md           # Quick start guide
├── modules/            # From TelegramTools
│   ├── media_downloader.py
│   ├── message_scraper.py
│   ├── user_export.py
│   ├── origin_tracer.py
│   ├── info.py
│   └── post_downloader.py
└── ai/
    └── schema.py       # AI agent schemas
```

# Music Bot (@whatsmusicbot) — Robust Integration

## Overview

@whatsmusicbot is a Telegram bot for finding music by name, link, or voice message.
Supports song search, lyrics, and download. Requires channel subscription.

**Source:** Custom integration built on Telethon. Located at `~/.agent-reach/tools/telegram-toolkit/music_bot.py`.

## Quick Start

```bash
cd ~/.agent-reach/tools/telegram-toolkit

# Search only
python3 music_bot.py search "Hello Adele"

# Download
python3 music_bot.py download "Hello Adele"

# Full flow (search + download + lyrics)
python3 music_bot.py full "Hello Adele" --output /tmp/

# JSON output
python3 music_bot.py search "Hello Adele" --json
```

## Python API

```python
import asyncio
from music_bot import MusicBot

async def main():
    bot = MusicBot()
    
    # Search — returns list of track buttons
    result = await bot.search("Hello Adele")
    # result = {text, buttons: [{text, data}], message_id}
    
    # Select track — clicks button, returns track info + download link
    result = await bot.select_track(message_id, button_index=0)
    # result = {text, buttons, message_id, track_info}
    
    # Download — downloads audio file
    result = await bot.download_track(message_id, output_dir="/tmp/")
    # result = {filename, size_mb, message_id}
    
    # Get lyrics
    result = await bot.get_lyrics(message_id)
    # result = {text, message_id}
    
    # Full flow — search + download + lyrics in one call
    result = await bot.full_search("Hello Adele")
    # result = {track_info, filename, size_mb, lyrics, search_results}
    
    await bot.disconnect()

asyncio.run(main())
```

## Subscription Handling

The bot requires joining 3 channels before use. The script handles this automatically:

1. Detects subscription message (buttons with `t.me/` URLs)
2. Joins each channel via `JoinChannelRequest`
3. Clicks `check_unified_sub` button to verify
4. Continues with search

**No manual intervention needed.**

## Rate Limits & Timing

| Operation | Delay | Notes |
|-----------|-------|-------|
| Between requests | 2s | Auto-enforced |
| After search | 10s | Wait for results |
| After button click | 2s | Wait for response |
| FloodWait | 1.5x wait | Auto-handled |
| Max retries | 3 | On timeout/error |
| Retry delay | 5s | Between retries |

## Supported Input Types

| Input | Example | Works |
|-------|---------|-------|
| Song name | `Hello Adele` | ✅ |
| Artist + Song | `Ed Sheeran Shape of You` | ✅ |
| Persian song | `تابستون کوتاه` | ✅ |
| YouTube link | `https://youtube.com/watch?v=...` | ✅ |
| Instagram link | `https://instagram.com/p/...` | ✅ |
| TikTok link | `https://tiktok.com/...` | ✅ |
| Lyrics text | `some lyrics text` | ✅ |

## Error Handling

| Error | Handling |
|-------|----------|
| FloodWait | Auto-sleep (1.5x wait time) |
| BotResponseTimeout | Retry up to 3 times |
| RPCError | Retry with backoff |
| No results | Return empty result |
| Subscription required | Auto-join channels |

## Pitfalls

1. **Subscription first:** Bot won't respond to clicks until you join channels AND click `check_unified_sub`.
2. **Button click timeout:** `GetBotCallbackAnswerRequest` raises `BotResponseTimeoutError` if bot is slow or subscription not verified.
3. **Rate limit between requests:** 2s minimum between any two requests to the same bot.
4. **2FA:** If account has 2FA enabled, `music_bot.py` will fail. Disable 2FA or provide password.
5. **Session shared:** Uses same `telegram.session` as `cli.py`. One login works for all tools.

## Integration with agent-reach

```bash
# From research script
~/.hermes/scripts/research-telegram.sh "music query"

# From CLI
python3 cli.py search "query" --channel @whatsmusicbot

# From Python
from music_bot import MusicBot
bot = MusicBot()
result = await bot.full_search("query")
```

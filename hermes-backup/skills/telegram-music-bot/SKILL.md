---
name: telegram-music-bot
description: >
  MUST USE when user wants to search, find, or download music from Telegram.
  Uses @whatsmusicbot — supports song names, lyrics, Instagram/TikTok/YouTube links.
  Handles subscription checks, rate limits, and retries automatically.
triggers:
  - music
  - آهنگ
  - موسیقی
  - download song
  - find music
  - دانلود آهنگ
  - پیدا کردن آهنگ
  - lyrics
  - متن ترانه
  - instagram music
  - tiktok music
  - youtube music
related_skills:
  - agent-reach
  - telegram-toolkit
platforms:
  - linux
required_commands:
  - python3
  - telethon
---

# Telegram Music Bot (@whatsmusicbot)

## Overview

@whatsmusicbot is a Telegram bot that finds music by:
- Song name / artist name
- Lyrics text
- Voice messages with music
- Video with music
- Instagram/TikTok/YouTube links

## Quick Start

```bash
cd ~/.agent-reach/tools/telegram-toolkit

# Search only
python3 music_bot.py search "Hello Adele"

# Download
python3 music_bot.py download "Hello Adele"

# Full (search + download + lyrics)
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
    
    # Search
    result = await bot.search("Hello Adele")
    # result = {text, buttons: [{text, data}], message_id}
    
    # Select track
    result = await bot.select_track(message_id, button_index=0)
    # result = {text, buttons, message_id, track_info}
    
    # Download
    result = await bot.download_track(message_id, output_dir="/tmp/")
    # result = {filename, size_mb, message_id}
    
    # Get lyrics
    result = await bot.get_lyrics(message_id)
    # result = {text, message_id}
    
    # Full flow (search + download + lyrics)
    result = await bot.full_search("Hello Adele")
    # result = {track_info, filename, size_mb, lyrics, search_results}
    
    await bot.disconnect()

asyncio.run(main())
```

## Rate Limits & Timing

| Operation | Delay | Notes |
|-----------|-------|-------|
| Between requests | 2s | Auto-enforced |
| After search | 10s | Wait for results |
| After button click | 2s | Wait for response |
| FloodWait | 1.5x wait | Auto-handled |
| Max retries | 3 | On timeout/error |
| Retry delay | 5s | Between retries |

## Subscription Handling

The bot requires joining 3 channels. The script handles this automatically:
1. Detects subscription message
2. Joins required channels
3. Clicks "check subscription" button
4. Continues with search

**No manual intervention needed.**

## Error Handling

| Error | Handling |
|-------|----------|
| FloodWait | Auto-sleep (1.5x wait time) |
| BotResponseTimeout | Retry up to 3 times |
| RPCError | Retry with backoff |
| No results | Return empty result |
| Subscription required | Auto-join channels |

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

## Troubleshooting

### Bot doesn't respond
```
Cause: Rate limit or subscription required
Fix: Wait 30s, then retry. Script auto-handles subscription.
```

### Timeout on button click
```
Cause: Bot slow or subscription not verified
Fix: Script retries 3 times automatically. Check subscription status.
```

### No download link
```
Cause: Track not available or region locked
Fix: Try different search query or artist name.
```

### FloodWait error
```
Cause: Too many requests
Fix: Script auto-sleeps. Wait for completion.
```

## File Locations

| File | Location |
|------|----------|
| Script | `~/.agent-reach/tools/telegram-toolkit/music_bot.py` |
| Session | `~/.agent-reach/tools/telegram-toolkit/telegram.session` |
| Config | `~/.agent-reach/tools/telegram-toolkit/config.yaml` |
| Downloads | `/tmp/` (default) |

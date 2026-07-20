# Telegram Toolkit

Full-featured Telegram automation toolkit.

## Features

- Search messages globally or in channels
- Download media (photos, videos, audio)
- Export messages to JSON/CSV
- Monitor channels in real-time
- Interact with bots (click buttons)
- Download music via @whatsmusicbot

## Quick Start

```bash
# Install dependencies
pip install telethon pyyaml

# Configure
cp config.yaml.example config.yaml
# Edit config.yaml with your API keys

# Login
python3 cli.py info @telegram
```

## CLI Commands

```bash
# Search
python3 cli.py search "query" --channel @channel

# Download
python3 cli.py download @channel --limit 100

# Export
python3 cli.py export @channel --format json

# Monitor
python3 cli.py monitor @channel

# Info
python3 cli.py info @channel
```

## Music Bot

```bash
# Search music
python3 music_bot.py search "Hello Adele"

# Download music
python3 music_bot.py download "Hello Adele"

# Full flow
python3 music_bot.py full "Hello Adele"
```

## Bot Interactor

```python
from bot_interactor import BotInteractor

bot = BotInteractor()
await bot.start()

# Send message and get buttons
result = await bot.send_and_wait('@bot', '/start')

# Click button
await bot.click_button(bot, msg_id, button_data)
```

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Messages/sec | 25 |
| Downloads/sec | 5 |
| FloodWait | Auto-handled |

## Credits

Built with:
- [Telethon](https://github.com/LonamiWebs/Telethon) - MTProto client
- [telegram_media_downloader](https://github.com/Dineshkarthik/telegram_media_downloader) - Bulk download
- [TelegramTools](https://github.com/DilshanHarshajith/TelegramTools) - Modular scraping

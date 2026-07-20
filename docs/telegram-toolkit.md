# Telegram Toolkit — Detailed Guide

## Overview

Telegram Toolkit provides full automation for Telegram.

## Installation

### Step 1: Get API Keys

1. Go to https://my.telegram.org/apps
2. Login with phone number
3. Create application
4. Copy `api_id` and `api_hash`

### Step 2: Configure

```bash
cd telegram-toolkit
cp config.yaml.example config.yaml
nano config.yaml
# Enter your api_id and api_hash
```

### Step 3: Install Dependencies

```bash
pip install telethon pyyaml
```

### Step 4: First Login

```bash
python3 cli.py info @telegram
# Enter phone number
# Enter verification code
# Session is saved automatically
```

## Usage

### Search Messages

```bash
# Global search
python3 cli.py search "AI agent"

# Channel search
python3 cli.py search "update" --channel @telegram

# With limit
python3 cli.py search "query" --limit 20

# JSON output
python3 cli.py search "query" --format ai
```

### Download Media

```bash
# Download photos
python3 cli.py download @channel --type photo

# Download videos
python3 cli.py download @channel --type video

# With limit
python3 cli.py download @channel --limit 100

# Custom output
python3 cli.py download @channel --output ~/downloads/
```

### Export Messages

```bash
# JSON format
python3 cli.py export @channel --format json

# CSV format
python3 cli.py export @channel --format csv

# With limit
python3 cli.py export @channel --limit 1000
```

### Monitor Channel

```bash
# Basic monitoring
python3 cli.py monitor @channel

# Custom interval
python3 cli.py monitor @channel --interval 30
```

### Get Info

```bash
# Channel info
python3 cli.py info @channel

# User info
python3 cli.py info @username
```

## Music Bot

### Search Music

```bash
python3 music_bot.py search "Hello Adele"
```

### Download Music

```bash
python3 music_bot.py download "Hello Adele"
```

### Full Flow

```bash
python3 music_bot.py full "Hello Adele" --output /tmp/
```

### Supported Inputs

| Input | Example |
|-------|---------|
| Song name | `Hello Adele` |
| Artist + Song | `Ed Sheeran Shape of You` |
| Persian song | `تابستون کوتاه` |
| YouTube link | `https://youtube.com/watch?v=...` |
| Instagram link | `https://instagram.com/p/...` |

## Bot Interactor

### Python API

```python
from bot_interactor import BotInteractor

bot = BotInteractor()
await bot.start()

# Send message
result = await bot.send_and_wait('@bot', '/start')

# Click button
await bot.click_button(bot, msg_id, button_data)

# Get buttons
buttons = await bot.list_buttons(bot, msg_id)
```

### Auto-Join Channels

```python
from auto_join import check_and_join

# Auto-join required channels
await check_and_join('@bot')
```

## Rate Limits

| Operation | Limit | Auto-Handle |
|-----------|-------|-------------|
| Messages/sec | 25 | ✅ |
| Downloads/sec | 5 | ✅ |
| FloodWait | 60s | ✅ |
| Retries | 3 | ✅ |

## Troubleshooting

### Login fails

```bash
# Delete session
rm -f telegram.session

# Try again
python3 cli.py info @telegram
```

### FloodWait error

Script auto-handles. Just wait.

### Bot timeout

Increase timeout in `music_bot.py`:
```python
BUTTON_CLICK_TIMEOUT = 30  # seconds
```

### No download link

Check if bot requires subscription:
```python
from auto_join import check_and_join
await check_and_join('@whatsmusicbot')
```

## Credits

Built with:
- [Telethon](https://github.com/LonamiWebs/Telethon) - MTProto client
- [telegram_media_downloader](https://github.com/Dineshkarthik/telegram_media_downloader) - Bulk download
- [TelegramTools](https://github.com/DilshanHarshajith/TelegramTools) - Modular scraping

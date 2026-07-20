# Telegram Bot Interaction — Inline Buttons & Callbacks

## Overview

Telethon can interact with Telegram bots that use inline keyboards (buttons).
This covers bots like @whatsmusicbot that require clicking buttons to navigate.

## Correct Imports (Pitfall)

The Telethon docs and many examples show `InlineKeyboardMarkup` — this does NOT
exist in Telethon 1.42+. The correct types are:

```python
# CORRECT:
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonCallback

# WRONG (causes ImportError):
from telethon.tl.types import InlineKeyboardMarkup, InlineKeyboardButton
```

## Core Pattern

### 1. Send message and get reply with buttons

```python
from telethon import TelegramClient
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

client = TelegramClient(session, api_id, api_hash)
await client.start()

# Send message
await client.send_message('@bot_username', '/start')

# Wait and get reply
import asyncio
await asyncio.sleep(2)
messages = await client.get_messages('@bot_username', limit=1)
msg = messages[0]

# Parse buttons
if msg.reply_markup:
    for row in msg.reply_markup.rows:
        for button in row.buttons:
            print(f"Text: {button.text}, Data: {button.data}")
```

### 2. Click a button

```python
# Click by data (bytes)
await client(GetBotCallbackAnswerRequest(
    '@bot_username',
    msg.id,
    data=b'lang:fa',  # button.data is bytes
))
```

### 3. Get response after click

```python
await asyncio.sleep(2)
response = await client.get_messages('@bot_username', limit=1)
print(response[0].text)
```

## Full BotInteractor Class

Located at `~/.agent-reach/tools/telegram-toolkit/bot_interactor.py`:

```python
from bot_interactor import BotInteractor

bot = BotInteractor()
await bot.start()

# Send and wait for reply
result = await bot.send_and_wait('@whatsmusicbot', '/start')
# result = {"text": "...", "buttons": [...], "message_id": 123}

# Click button by data
result = await bot.click_button('@whatsmusicbot', msg_id, b'lang:fa')

# Click button by text
result = await bot.click_button_by_text('@whatsmusicbot', msg_id, '🇬🇧 English')

# List buttons
buttons = await bot.list_buttons('@whatsmusicbot', msg_id)
```

## CLI Usage

```bash
# Single interaction
python3 bot_interactor.py @whatsmusicbot --message "/start" --json

# Interactive session (click by number)
python3 bot_interactor.py @whatsmusicbot --interactive
```

## Bot Subscription Pattern (CRITICAL)

Many bots require joining channels before they work. This is the #1 cause of
`BotResponseTimeoutError` — the bot silently ignores button clicks if you
haven't joined its required channels.

### Detection

After `/start`, if the bot replies with:
- Text containing "مشترک" (Persian) or "subscribe" or "join"
- URL buttons (`data=None`) pointing to `t.me/+...` links
- A "check subscription" button with `data=b'check_unified_sub'`

→ The bot requires channel subscription.

### Auto-join Pattern

```python
from telethon.tl.functions.channels import JoinChannelRequest

# 1. Get subscription message buttons
for btn in buttons:
    if btn.url and 't.me/' in btn.url:
        entity = await client.get_entity(btn.url)
        await client(JoinChannelRequest(entity))
        await asyncio.sleep(1)

# 2. Click "check subscription" button
await client(GetBotCallbackAnswerRequest(
    bot_username, msg_id, data=b'check_unified_sub'
))
```

### Full Script

Use `auto_join.py` for automatic handling:

```bash
cd ~/.agent-reach/tools/telegram-toolkit
python3 auto_join.py @whatsmusicbot
```

### music_bot.py

The `music_bot.py` script handles subscription automatically in `search()`:
1. Sends search query
2. Checks for subscription message
3. Joins required channels
4. Clicks "check subscription"
5. Returns search results

No manual intervention needed.

## Common Bot Patterns

### @whatsmusicbot (Music Search)
1. `/start` → language selection (21 buttons)
2. Click `lang:fa` → main menu
3. Send song name → results as buttons
4. Click result → download

### General Bot Workflow
1. `/start` → get initial buttons
2. Click target button → get new state
3. Send input if needed → get results
4. Click result button → get content

## Callback Data Format

Bots encode actions in callback_data (bytes):
- `lang:fa` → language selection
- `search:query` → search action
- `dl:12345` → download specific item
- `page:2` → pagination

Always check `button.data.decode()` to see the actual format.

## Rate Limits

Bot interactions are subject to Telegram's flood limits:
- ~30 callbacks/sec safe
- FLOOD_WAIT applies if exceeded
- Telethon auto-sleeps for short waits

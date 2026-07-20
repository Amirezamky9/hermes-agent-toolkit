# Telegram via Telethon — MTProto Integration

## Overview

Telethon is a Python library for Telegram's MTProto protocol. Unlike HTTP cookie-based
platforms (Twitter, Reddit, YouTube), Telegram uses a direct connection to its servers.

**Key difference:** No HTTP cookies. Auth uses `api_id` + `api_hash` + phone number.
Session is stored in `.session` files (SQLite), not cookie JSON.

## Setup

### 1. Get API Keys

Go to https://my.telegram.org/apps and create an application:
- **App title:** Agent Reach (or any name)
- **Short name:** agentreach
- **Platform:** Other

You'll get `api_id` (numeric) and `api_hash` (string).

### 2. Save Credentials

```bash
cat > ~/.agent-reach/cookies/telegram.env << 'EOF'
TG_API_ID=your_numeric_id
TG_API_HASH=your_api_hash
EOF
chmod 600 ~/.agent-reach/cookies/telegram.env
```

### 3. Install Telethon

```bash
pip install telethon
```

### 4. First Login

Login requires phone number + SMS code. Two-step process for non-interactive sessions:

```bash
cd ~/.agent-reach/tools/telegram-toolkit

# Step 1: Send code request
python3 step1_send_code.py

# Step 2: Enter code and sign in
echo "12345" > .login_code
python3 step2_sign_in.py
```

Session saved to `telegram.session` (SQLite). Valid for 3-6 months.

## Core Concepts

### Session Management

```python
from telethon import TelegramClient

client = TelegramClient('session_name', api_id, api_hash)
await client.start()  # Interactive (needs input())
await client.start(phone='+1234567890')  # Non-interactive
```

### Rate Limits

| Operation | Limit | Auto-handle |
|-----------|-------|-------------|
| Search | 30 req/sec | Telethon auto-throttles |
| Download | ~50 files → FLOOD_WAIT 60s | Auto-sleep |
| Send messages | 30 msg/sec (userbot) | Manual |
| Join groups | 50/day | Manual |

### FloodWait Handling

```python
from telethon.errors import FloodWaitError

try:
    await client.send_message(entity, text)
except FloodWaitError as e:
    print(f"Sleeping {e.seconds}s")
    await asyncio.sleep(e.seconds)
```

## Common Operations

### Search Messages

```python
# Global search
async for message in client.iter_messages(None, search='query', limit=10):
    print(message.text)

# Channel search
async for message in client.iter_messages('@channel', search='query', limit=10):
    print(message.text)
```

### Download Media

```python
async for message in client.iter_messages('@channel', limit=100):
    if message.media:
        await client.download_media(message, file='downloads/')
```

### Get Channel Info

```python
entity = await client.get_entity('@channel')
print(entity.title)
print(entity.participant_count)
```

### Get User Info

```python
user = await client.get_entity('@username')
print(user.first_name)
print(user.username)
```

## Toolkit CLI

The unified CLI at `~/.agent-reach/tools/telegram-toolkit/cli.py` wraps all operations:

```bash
python3 cli.py search "query" --channel @name
python3 cli.py download @name --limit 100
python3 cli.py export @name --format json
python3 cli.py monitor @name
python3 cli.py info @name
```

## Pitfalls

1. **No HTTP cookies** — Telegram uses MTProto, not HTTP. Don't look for `telegram-cookies.json`.
2. **Session expiry** — Sessions expire after 3-6 months. Re-login required.
3. **Phone number required** — First login needs phone + SMS code.
4. **2FA** — If enabled, password is required after SMS code.
5. **FloodWait** — Too many requests → temporary ban. Respect rate limits.
6. **Cross-DC files** — Files on different data centers may be slower to download.
7. **Inline keyboard types** — Use `ReplyInlineMarkup` + `KeyboardButtonCallback`, NOT `InlineKeyboardMarkup`. The latter doesn't exist in Telethon's `tl.types`.
8. **Non-interactive login** — `client.start()` calls `input()` internally. In non-interactive sessions (scripts, subagents), use the two-step pattern: `send_code_request()` → save `phone_code_hash` → `sign_in(phone, code, phone_code_hash=hash)`.
9. **BotResponseTimeoutError** — `GetBotCallbackAnswerRequest` times out if bot requires channel subscription. Run `auto_join.py` first.
10. **Credential resolution order** — `modules/config.py` reads: config.yaml → telegram.env → .env → env vars → interactive prompt. Put API keys in `~/.agent-reach/cookies/telegram.env` or toolkit's `config.yaml`.

## References

- [Telethon Documentation](https://docs.telethon.dev/)
- [Telegram API](https://core.telegram.org/api)
- [MTProto](https://core.telegram.org/mtproto)

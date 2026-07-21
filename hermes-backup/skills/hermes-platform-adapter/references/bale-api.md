# Bale (بله) Bot API — Condensed Reference

Bale is an Iranian messaging platform. Its Bot API is ~95% compatible with
Telegram Bot API. This document covers the differences only.

## Key Differences from Telegram

| Aspect | Telegram | Bale |
|--------|----------|------|
| Base URL | `https://api.telegram.org/bot<token>/` | `https://tapi.bale.ai/bot<token>/` |
| File download | `https://api.telegram.org/file/bot<token>/<path>` | `https://tapi.bale.ai/file/bot<token>/<path>` |
| Webhook ports | 443, 80, 88, 8443 | 443, 88 |
| Update storage | Unlimited (recent) | 2000 messages, 24 hours |
| Token format | Same (`<bot_id>:<alphanumeric>`) | Same |

## Extra Methods (Not in Telegram)

- **`askReview`** — Request a satisfaction survey from the user. Added in
  Aban 1404 (Oct-Nov 2025). Only works on new client versions.
- **`inquireTransaction`** — Query transaction status by ID. Returns a
  `Transaction` object. Not in standard Telegram bot libraries; must be
  called via direct HTTP.

## Bot Creation

1. Chat with `@botfather` on Bale: https://ble.ir/botfather
2. Send `/newbot`
3. Follow prompts to set name and username
4. Receive token in format `123456789:ABC123...`

## Markdown Formatting

Bale supports Markdown (NOT MarkdownV2 like Telegram):
- **Bold**: `*text*` (asterisks, not double)
- **Italic**: `_text_` (underscores)
- **Links**: `[text](url)`
- **Spoilers**: `||text||`
- **Code**: `` `code` ``
- **Pre-formatted**: ` ```code``` `
- **Hover text**: ` ```[text]tooltip``` ` (Bale-specific)

## File Handling

- Max upload via multipart: 50MB (documents), 10MB (images)
- Max via URL: 20MB (non-image), 5MB (image)
- `file_id` is bot-specific (cannot transfer between bots)
- File download links valid for 1 hour

## Supported Types

User, Chat, ChatFullInfo, Message, MessageId, MessageEntity, PhotoSize,
Animation, Audio, Document, Video, Voice, Contact, Location, Invoice, File,
ReplyKeyboardMarkup, InlineKeyboardMarkup, CallbackQuery, WebAppData,
WebAppInfo, Sticker, StickerSet, ChatMember (4 types), ChatPhoto,
InputMedia (5 types), InputFile

## Mini Apps

Bale supports Mini Apps (similar to Telegram Mini Apps):
- Main mini app (set via @botfather)
- Inline button web_app field
- Reply keyboard web_app field
- Menu button mini app
- JavaScript SDK: `window.Bale.WebApp`
- Data validation via HMAC-SHA-256

## Payment System

- Uses Bale's electronic wallet (کیف پول الکترونیکی)
- Three wallet types: personal, business, organizational
- Test token: `WALLET-TEST-1111111111111111`
- Methods: `sendInvoice`, `createInvoiceLink`, `answerPreCheckoutQuery`

## Python Usage (httpx example)

```python
import httpx

TOKEN = "1275588422:ABC..."
BASE = f"https://tapi.bale.ai/bot{TOKEN}"

# getMe
r = httpx.get(f"{BASE}/getMe").json()

# sendMessage
r = httpx.post(f"{BASE}/sendMessage", json={
    "chat_id": 66881162,
    "text": "Hello from Bale!"
}).json()

# getUpdates (long polling)
r = httpx.get(f"{BASE}/getUpdates", params={
    "offset": 0,
    "timeout": 30
}).json()
```

## Tested Configuration

- Bot: @event_rosteri_bot (ID: 1275588422)
- Chat ID: 66881162
- Adapter created: `~/.hermes/plugins/platforms/bale/`
- All basic operations verified (getMe, getUpdates, sendMessage)

# Telegram Managed Bots (Bot API 9.6+)

> Discovered: July 2026  
> Source: telegram.org/blog, core.telegram.org/bots/api, core.telegram.org/bots/features

## What It Is

**Managed Bots** (introduced in Bot API 9.6 — April 3, 2026) allow a **Manager Bot** to create and control
other bots on behalf of users. The child bots run on Telegram's own infrastructure — **no server needed**
from the end user's perspective.

## Key Concepts

| Term | Meaning |
|------|---------|
| **Manager Bot** | A regular bot with "Bot Management Mode" enabled in BotFather |
| **Managed Bot** | A child bot provisioned for a specific user by the manager |
| **Creation Link** | `https://t.me/newbot/{manager_username}/{suggested_username}?name={suggested_name}` |

## How the Flow Works

1. Create a bot via BotFather, enable **"Bot Management Mode"** in BotFather's MiniApp
2. Share a creation link: `https://t.me/newbot/ManagerBot/suggested_username?name=SuggestedName`
3. User clicks the link → Telegram provisions a new bot for that user
4. Manager bot receives a `ManagedBotUpdated` update (field `managed_bot` on the `Update` object)
5. Call `getManagedBotToken(child_bot_id)` to get the child bot's token
6. Use that token to call any Bot API method on behalf of the child bot

## Key API Methods

| Method | Purpose |
|--------|---------|
| `getManagedBotToken` | Get the token of a managed child bot |
| `replaceManagedBotToken` | Replace the token (rotate credentials) |
| `KeyboardButtonRequestManagedBot` | Add a "request managed bot" button |
| `savePreparedKeyboardButton` | Save a prepared button for reuse |
| `answerChatJoinRequestQuery` | Handle join request queries (Guardian Bots) |
| `sendChatJoinRequestWebApp` | Launch a Web App for join request screening |

## Update Types

- `managed_bot` field on `Update` → `ManagedBotUpdated` object
- `managed_bot_created` field on `Message` → `ManagedBotCreated` object
- `can_manage_bots` field on `User` → whether user can manage bots

## No-Code AI Bot Builder

The Managed Bots mechanism enables services like @teleclaw_bot (OpenClaw), Telewer, GPTBots, and Lazy AI
to offer **zero-code AI bot creation**:

1. User clicks a link → personal bot instance created
2. User connects the bot to an AI platform (GPT, Llama via Telewer/Lazy AI)
3. AI bot answers messages, handles tasks — all on Telegram infra
4. **No hosting, no server setup, no API key management** for the end user

## Bot-to-Bot Communication (Bot API 10.0 — May 8, 2026)

Bots can now talk to each other. Enable "Bot-to-Bot Communication Mode" in BotFather.
Key updates:
- `supports_guest_queries` field on `User`
- `guest_message` field on `Update` (Guest Mode)
- `answerGuestQuery` method — bots can reply in chats they're not members of

## Sources

- https://telegram.org/blog/ai-editor-mighty-polls-and-more (Mar 31, 2026 — Managed Bots announcement)
- https://telegram.org/blog/ai-bot-revolution-11-new-features (May 7, 2026 — Guest Bots + Bot-to-Bot)
- https://core.telegram.org/bots/features#managed-bots
- https://core.telegram.org/bots/api (Bot API 9.6 changelog)

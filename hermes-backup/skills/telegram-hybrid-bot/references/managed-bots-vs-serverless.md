# Managed Bots vs Telegram Serverless — Key Differences

A common confusion: Managed Bots (Bot API 9.6, April 2026) and Telegram
Serverless (summer 2026) are **separate features** with different purposes,
tokens, and activation paths.

## At a Glance

| Feature | Managed Bots | Telegram Serverless |
|---------|-------------|-------------------|
| What it does | Lets a bot **create** child bots | Lets a bot **run code** on TG infra |
| API level | Bot API 9.6 (April 3, 2026) | Post-10.1 (newer) |
| Token type | Bot API token (`723456:AAH...`) | CLI token (`app<id>:<secret>`) |
| Where to activate | No activation — just use the API | Must toggle ON in BotFather per-bot |
| Use case | User wants to deploy bots without /newbot | User wants to run backend code serverless |
| Can it bypass Serverless activation? | ❌ No — even with the child's API token, Serverless isn't enabled on that bot | N/A |

## Can Managed Bots provide a CLI token for Serverless?

**No.** The two tokens serve different purposes:

```
getManagedBotToken() → Bot API token
                          ↓
              Used for calling Bot API methods
              (sendMessage, getUpdates, etc.)
                          ↓
              CANNOT log in to tgcloud CLI
              CANNOT enable Serverless on the child bot

CLI Access Token (from BotFather → Serverless)
                          ↓
              Used for `npx tgcloud login`
              Authorizes `tgcloud push` / `migrate` / `run`
```

Even if you get a child bot's API token via Managed Bots, you still need to
open that child bot in BotFather and manually enable Serverless to get its
CLI token. There is **no API method** to enable Serverless or retrieve the
CLI token programmatically — it's BotFather-only today.

## What Managed Bots CAN do

- Let a Manager Bot create child bots via
  `https://t.me/newbot/{manager}/{suggested_username}[?name={name}]`
- Get the child's token: `getManagedBotToken(user_id)`
- Replace the child's token: `replaceManagedBotToken(user_id)`
- Manage access: `getManagedBotAccessSettings(user_id)`,
  `setManagedBotAccessSettings(user_id, is_access_restricted, added_user_ids)`
- Receive updates when a managed bot is created or its token changes (via
  ManagedBotUpdated update type)

## What Telegram Serverless CAN do

- Run JS modules (handlers) on Telegram's infrastructure
- Provide a built-in SQLite database per bot
- Call external APIs via `sdk/fetch`
- Full Bot API access: `sdk/api.sendMessage(...)`

They are complementary, not replacements. A Serverless bot could use
Managed Bots API calls to create child bots for users. But they solve
different problems.

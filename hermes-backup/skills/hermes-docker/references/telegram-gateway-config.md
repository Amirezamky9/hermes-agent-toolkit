# Telegram Gateway Config Reference

Discovered from `plugins/platforms/telegram/adapter.py` and `gateway/config.py`.

## Config.yaml structure

Under `gateway.platforms.telegram`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | bool | false | Enable Telegram platform |
| `token` | str | -- | Bot token (also in `.env` as `TELEGRAM_BOT_TOKEN`) |
| `reply_to_mode` | str | "first" | Threading: "off", "first", or "all" |
| `typing_indicator` | bool | true | Show "typing..." while processing |
| `gateway_restart_notification` | bool | true | Send "Gateway online" on restart |
| `home_channel` | dict | -- | Default delivery target: {platform, chat_id, name, thread_id?} |
| `extra` | dict | {} | Platform-specific settings (see below) |

The `home_channel` config block specifies where cron job results and cross-platform messages are delivered when no explicit destination is given, and drives the "♻ Gateway online" startup notification. Example:
```yaml
home_channel:
  platform: telegram
  chat_id: "943724562"
  name: "Your Name"
```

**⚠️ Important — two separate mechanisms.** The "No home channel is set" banner (shown at the start of every new Telegram session) checks the **`TELEGRAM_HOME_CHANNEL` env var** in the process environment (read from `.env` at startup), NOT the `home_channel:` YAML block. To suppress the banner you must set the env var — config.yaml alone is not enough. The `/sethome` command writes to both (`.env` + in-memory config), so running it once fixes everything. Equivalent manual fix:

```bash
# In .env — suppresses the "/sethome" banner
TELEGRAM_HOME_CHANNEL=943724562
TELEGRAM_HOME_CHANNEL_THREAD_ID=466114

# In config.yaml — enables startup notifications
gateway.platforms.telegram.home_channel:
  platform: telegram
  chat_id: "943724562"
  name: "Your Name"
```

## Extra config options

Under `extra:`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `allow_from` | list[str] | [] | User IDs allowed to use the bot |
| `allowed_chats` | list | [] | Chat IDs allowed to interact |
| `group_allowed_chats` | list | [] | Group chat IDs allowed |
| `allowed_topics` | list | [] | Topic IDs allowed in forum groups |
| `ignored_threads` | list | [] | Thread IDs to ignore |
| `guest_mode` | bool | false | Let unlisted users send limited messages |
| `require_mention` | bool | false | Only respond when bot is @-mentioned |
| `observe_unmentioned_group_messages` | bool | false | Read but don't respond |
| `ingest_unmentioned_group_messages` | bool | false | Include unmentioned msgs in context |
| `exclusive_bot_mentions` | bool | false | Only read @-mentions in groups |
| `free_response_chats` | list | [] | Chats where bot responds without mention |
| `mention_patterns` | list | [] | Custom regex patterns for activation |
| `group_sessions_per_user` | bool | true | Separate sessions per user in groups |
| `thread_sessions_per_user` | bool | false | Separate sessions per DM topic thread |
| `dm_topics` | list[dict] | [] | DM topic config: [{name, chat_id}] |
| `base_url` | str | — | Custom Bot API endpoint |
| `base_file_url` | str | — | Custom file endpoint |
| `local_mode` | bool | false | Local Bot API server mode |
| `fallback_ips` | list[str] | [] | Static fallback IPs for api.telegram.org |
| `ignore_root_dm` | bool | false | Ignore root DM (force topic use) |
| `status_indicator` | bool | false | Show online/offline status |
| `status_online` | str | "Online" | Status text when online |
| `status_offline` | str | "Offline" | Status text when offline |

## DM Topics Setup

DM topics (also called "private chat topics") let a single user run multiple independent sessions with Hermes in one chat. Each topic gets its own `message_thread_id` and acts as a separate conversation.

Config in `config.yaml`:
```yaml
gateway:
  platforms:
    telegram:
      extra:
        thread_sessions_per_user: true
        dm_topics:
          - name: "default"
            chat_id: "943724562"
          - name: "work"
            chat_id: "943724562"
```

The topics are created at startup in the user's private chat. The `/topic` slash command manages them.

## Env vars summary

| Env var | Source | Overrides |
|---------|--------|-----------|
| `TELEGRAM_BOT_TOKEN` | `.env` | Token from config.yaml |
| `TELEGRAM_ALLOWED_USERS` | `.env` | Comma-separated user IDs |
| `TELEGRAM_GROUP_ALLOWED_USERS` | `.env` | Separate group allowlist |
| `TELEGRAM_ALLOW_ALL_USERS` | `.env` | "true"/"1" to allow anyone |
| `GATEWAY_ALLOW_ALL_USERS` | `.env` | Global allow-all override |
| `TELEGRAM_HOME_CHANNEL` | `.env` | Default delivery chat ID |
| `TELEGRAM_HOME_CHANNEL_NAME` | `.env` | Display name for home channel |
| `TELEGRAM_HOME_CHANNEL_THREAD_ID` | `.env` | Thread ID for home channel |
| `TELEGRAM_REPLY_TO_MODE` | `.env` | "off"/"first"/"all" |
| `TELEGRAM_FALLBACK_IPS` | `.env` | Comma-separated IPs |
| `TELEGRAM_PROXY` | `.env` | Proxy URL for Telegram API |

## Gateway log locations

- Gateway: `$HERMES_HOME/logs/gateway.log`
- PID file: `$HERMES_HOME/gateway.pid`
- Lock file: `$HERMES_HOME/gateway.lock`
- Kanban dispatcher lock: `$HERMES_HOME/kanban/.dispatcher.lock`

## Adapter code structure

The Telegram adapter (`plugins/platforms/telegram/adapter.py`, ~8400 lines) registers via `register()` at module bottom. Key classes:

- `TelegramAdapter(BasePlatformAdapter)` — main adapter class
- `TelegramFallbackTransport` — DNS fallback transport for api.telegram.org
- Config schema: `gateway/config.py` → `PlatformConfig` dataclass
- Plugin manifest: `plugins/platforms/telegram/plugin.yaml` (declares env vars)

The adapter uses `python-telegram-bot` v22.x with `Application.builder().token()` for polling.

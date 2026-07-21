# Monitoring Telegram Serverless Rollout

## Context

As of mid-July 2026, Telegram Serverless (`@tgcloud/cli` packages published
July 12) is in **silent gradual rollout** with zero public discussion. Many
bots do not show the Serverless option in BotFather. To be the first to know
when it's available for a specific bot, set up a daily watch.

## Cron Job Setup

```bash
# 1. The monitoring script ships with this skill:
skill_view(name="telegram-hybrid-bot", file_path="scripts/check-serverless-status.sh")

# 2. Create a non-agent cron job (no LLM token cost, silent when no change):
cronjob action=create \
  name="telegram-serverless-watch" \
  schedule="0 10 * * *" \
  script="telegram-hybrid-bot/check.sh" \
  no_agent=true

# Output behavior:
# - No change: script prints nothing → cron sends nothing → user sees silence
# - Change detected: script prints alert → cron delivers it to the user
```

## What the Script Checks

| Source | Check | Frequency |
|--------|-------|-----------|
| npm | Version bumps for `@tgcloud/cli` and `@tgcloud/create-bot` | Per run |
| Official docs | MD5 hash change — catches content updates | Per run |
| Reddit r/Telegram | New posts mentioning serverless or tgcloud | Per run (last week) |
| GitHub | New repos mentioning tgcloud | Per run |
| Hacker News | New stories about telegram serverless | Per run (last week) |

## When It Fires

The script delivers a message with all changes concatenated when _any_ source
shows new activity. Typical first trigger: an npm version bump or a Reddit
post appearing after initial absolute silence.

## Timeline (as of July 14, 2026)

| Date | Event |
|------|-------|
| July 12 | `@tgcloud/cli` 0.1.0 published |
| July 12 | `@tgcloud/create-bot` 0.1.0 published |
| July 13 | `@tgcloud/cli` 0.1.2 published (bugfix) |
| July 14 | Still no public discussion anywhere |

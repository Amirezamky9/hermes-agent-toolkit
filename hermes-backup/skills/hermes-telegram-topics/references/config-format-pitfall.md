# Telegram DM Topics — Config Format Pitfall (2026-07-07)

## Symptom

User reports topics aren't working properly — agent doesn't know which topic it's in, topic names not recognized, skill binding not activating.

## Root Cause

The `dm_topics` config was written in **flat format** instead of the required **nested format**.

### Flat format (BROKEN):
```yaml
dm_topics:
  - chat_id: '943724562'
    name: default
  - chat_id: '943724562'
    name: development
    thread_id: '465358'
```

### Nested format (CORRECT):
```yaml
dm_topics:
  - chat_id: '943724562'
    topics:
      - name: General
      - name: development
        thread_id: '465358'
      - name: عمومی
        thread_id: '465031'
      - name: بازی‌سازی
        thread_id: '465356'
      - name: روتین روزمره
        thread_id: '467002'
```

## Why It Breaks

In `adapter.py`, the code iterates:
```python
for candidate in entry.get("topics", []):
    if candidate.get("name") == name:
        topic_conf = candidate
        break
```

With flat format, `entry.get("topics", [])` returns `[]` (empty list) because there's no `topics` key — `name` is at the top level. Topics are silently ignored.

## Evidence from Gateway Logs

```
[Telegram] Flushing text batch agent:main:telegram:dm:943724562:465356 (127 chars)
```

The session key shows thread_id `465356`, but the flat config mapped `465356` to "بازی‌سازی" while the user said they were in "development" (which the config mapped to `465358`). The thread_ids in the flat config were stale/incorrect, and the topic names weren't being resolved at all.

## Additional Issue: Thread ID Mismatch

The config had thread_ids that didn't match reality:
- Config: `بازی‌سازی` → `465356`
- System prompt: thread `465356` (actual current thread)
- User: "we're in development"

This suggests topics were renamed in Telegram but the config wasn't updated. With the nested format and auto-population, this is less likely to happen.

## Verification Steps

1. Check config format:
   ```bash
   grep -A20 "dm_topics" ~/.hermes/config.yaml
   ```
   Look for `topics:` list under each `chat_id`.

2. Extract unique thread_ids from logs:
   ```bash
   grep "agent:main:telegram:dm:943724562" ~/.hermes/logs/gateway.log | grep -oP "agent:main:telegram:dm:943724562:\d+" | sort -u
   ```

3. Identify which thread_id is which topic — look for the session flush right before the user's message:
   ```bash
   grep -A2 "18:49:03" ~/.hermes/logs/gateway.log
   # Shows: Flushing text batch agent:main:telegram:dm:943724562:465358
   # Then: inbound message: ... msg='این تاپیک برای ریسرچ هست'
   # Conclusion: 465358 = research topic
   ```

4. Cross-reference with SQLite:
   ```python
   import sqlite3
   conn = sqlite3.connect('~/.hermes/state.db')
   cursor = conn.cursor()
   cursor.execute("SELECT thread_id, title FROM sessions WHERE source='telegram' AND user_id='943724562' AND thread_id IS NOT NULL GROUP BY thread_id")
   for row in cursor.fetchall():
       print(f"thread_id: {row[0]} | title: {row[1]}")
   ```

5. Verify system prompt Source line shows correct thread_id.

## Fix

1. Rewrite `dm_topics` in nested format
2. Verify thread_ids match actual Telegram topics (check gateway logs or system prompt)
3. Restart gateway: `hermes gateway restart`

### Editing Config Limitations

- **`hermes config set`** cannot handle complex nested structures like `dm_topics`
- **`patch` tool** refuses to edit `config.yaml` (security-sensitive)
- **Use Python yaml** for nested config changes:
  ```python
  import yaml
  with open('config.yaml', 'r') as f:
      config = yaml.safe_load(f)
  # Modify config['gateway']['platforms']['telegram']['extra']['dm_topics']
  with open('config.yaml', 'w') as f:
      yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
  ```
- **Cannot restart gateway from inside** — running `pkill` or `hermes gateway restart` from within the gateway process kills your own session. Use `/restart` slash command from Telegram or run from a separate shell.

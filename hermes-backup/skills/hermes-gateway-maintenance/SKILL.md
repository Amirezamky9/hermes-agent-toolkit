---
name: hermes-gateway-maintenance
description: "Diagnose and recover Hermes Gateway — crash recovery, silent PID death, platform connectivity checks, log analysis, and health monitoring."
version: 1.0.0
author: agent
metadata:
  hermes:
    tags: [hermes, gateway, troubleshooting, recovery, telegram, platforms]
    related_skills: [hermes-agent]
---

# Hermes Gateway Maintenance

Diagnose and fix common gateway failures on Hermes Agent, especially the "silent crash" pattern where the PID file is stale and messaging platforms (Telegram, Discord, etc.) stop responding while the WebUI stays healthy.

## Quick Recovery

```bash
# Gateway died? Restart with --replace to claim the stale PID file
hermes gateway run --replace

# Or via the hermes binary
cd ~/.hermes && \
PYTHONPATH=$HOME/.hermes/hermes-agent \
/app/venv/bin/python3 -m hermes_cli.main gateway run --replace
```

The `--replace` flag is **required** when a stale `gateway.pid` exists — without it, the gateway refuses to start with "already running".

## Diagnosis Checklist

### 1. Is the gateway process alive?

```bash
# Extract PID from the JSON PID file and check it
python3 -c "
import json
with open('$HOME/.hermes/gateway.pid') as f:
    d = json.load(f)
print(f'PID: {d[\"pid\"]}, kind: {d[\"kind\"]}')
" && kill -0 $(python3 -c "import json; print(json.load(open('$HOME/.hermes/gateway.pid'))['pid'])") 2>&1 && echo "ALIVE" || echo "DEAD"
```

### 2. When did the gateway last process anything?

```bash
# Recent activity — look for "inbound message:" lines
grep "inbound message:" ~/.hermes/logs/gateway.log | tail -3

# Last response timestamp
grep "Sending response" ~/.hermes/logs/gateway.log | tail -1

# Errors around the crash time
grep -A5 -B2 "ERROR\|Traceback" ~/.hermes/logs/gateway.log | tail -40
```

### 3. Hallmarks of a stale (dead) gateway

- WebUI (server.py HTTP on port 9999) responds normally
- Telegram/Discord/Slack stop responding
- `/platforms` slash command shows nothing or times out
- `gateway.log` tail ends hours ago — no recent `inbound message:` or `Sending response`
- `gateway.pid` contains a valid JSON dict but `kill -0` says "No such process"
- `gateway-exit-diag.log` shows recent exit_nonzero entries

### 4. Log file anatomy

```
~/.hermes/logs/
├── gateway.log                 # Main runtime — INFO+ messages, tracebacks
├── gateway-exit-diag.json      # JSON records of each gateway start/stop
└── gateway-shutdown-diag.log   # SIGTERM diagnostics (loadavg, process tree)
```

### 5. Common exit codes

| Exit code | Label | Meaning |
|-----------|-------|---------|
| 0 | exit_clean | Normal shutdown (intentional stop) |
| 1 | exit_nonzero | Unexpected crash — check gateway.log traceback |
| 1 (signal-initiated) | exit_nonzero | SIGTERM without restart request — systemd Restart=on-failure will revive it |

## Platform Health Checks

### Telegram

```bash
# Check connection
grep "telegram connected\|telegram disconnected\|Connecting to Telegram" ~/.hermes/logs/gateway.log | tail -5

# Check for recent message activity
grep "inbound message:.*telegram.*chat=" ~/.hermes/logs/gateway.log | tail -5

# Check send errors
grep -i "error sending\|telegram.*error\|failed.*telegram" ~/.hermes/logs/gateway.log | tail -5
```

Telegram uses polling mode (not webhook) by default. It first discovers fallback IPs via DNS-over-HTTPS, then connects. If it can't reach the Telegram API, check:
- DNS resolution
- Outbound access to `api.telegram.org` (or the discovered fallback IP)
- Bot token validity (check config.yaml `gateway.platforms.telegram.token`)

### Webhook

```bash
grep "webhook.*connected\|webhook.*Listening\|webhook.*error" ~/.hermes/logs/gateway.log | tail -5
```

## Crash Prevention

### Cron liveness check

Set up a cron job that checks the gateway PID periodically and restarts if dead:

```bash
# Create a liveness script
cat > ~/.hermes/scripts/gateway-healthcheck.sh << 'EOF'
#!/bin/bash
pid_file="$HOME/.hermes/gateway.pid"
if [ ! -f "$pid_file" ]; then
  echo "NO PID FILE — gateway never started or was fully cleaned"
  exit 0
fi
pid=$(python3 -c "import json; print(json.load(open('$pid_file'))['pid'])" 2>/dev/null)
if [ -z "$pid" ]; then
  echo "PID FILE MALFORMED"
  exit 0
fi
if kill -0 "$pid" 2>/dev/null; then
  echo "alive"
  exit 0
fi
echo "Gateway PID $pid is dead — restarting"
cd "$HOME/.hermes"
PYTHONPATH="$HOME/.hermes/hermes-agent" /app/venv/bin/python3 -m hermes_cli.main gateway run --replace 2>&1
EOF
chmod +x ~/.hermes/scripts/gateway-healthcheck.sh

# Then create a cron job to run it every 30 minutes
```

Or use a cron prompt:

```text
Check if gateway is alive by inspecting ~/.hermes/gateway.pid. 
If dead, restart with gateway run --replace. Report outcome.
```

### Safe restart pattern

```bash
# Preferred: stop then run with --replace
hermes gateway stop && hermes gateway run --replace

# Or combined:
hermes gateway stop; sleep 2; hermes gateway run --replace &
```

⚠️ **Do NOT use `hermes gateway restart` in non-systemd environments.**
It stops the gateway but the start phase can timeout or fail silently,
leaving ALL platforms (Telegram, Discord, etc.) dead. If you must use it,
always verify afterwards with `hermes gateway status` and have a recovery
command ready: `hermes gateway run --replace`.

## Process Recovery Walkthrough

Full step-by-step from the live session that produced this skill:

1. User reported Telegram not responding
2. Checked `~/.hermes/logs/gateway.log` — last activity was 3 days ago
3. Checked `~/.hermes/gateway.pid` — contained `{"pid": 98723, ...}` — but `kill -0 98723` returned "No such process"
4. WebUI server at port 9999 was healthy (Python HTTP server, PID 115)
5. No running `hermes` or `gateway` processes in `/proc/*/cmdline`
6. **Fix:** ran `cd ~/.hermes && PYTHONPATH=$HOME/.hermes/hermes-agent /app/venv/bin/python3 -m hermes_cli.main gateway run --replace`
7. Verified: `grep "telegram connected" ~/.hermes/logs/gateway.log | tail -1` → success

## Disabling / Enabling a Platform

To disable a messaging platform (e.g. Bale) without removing its plugin:

1. **Toggle the platform switch:**
   ```bash
   hermes config set gateway.platforms.<name>.enabled false
   ```
   ⚠️ The key path is `gateway.platforms.<name>.enabled`, NOT `platforms.<name>.enabled`.
   The latter creates a duplicate YAML key that the gateway ignores.

2. **Remove the plugin from the enabled list** (if present):
   Edit `plugins.enabled` in `config.yaml` to remove `platforms/<name>`.
   `config set` cannot reliably remove individual items from YAML arrays —
   use `hermes config edit` or `skill_manage` (patch) for array edits.

3. **Restart the gateway** (use the safe pattern above, NOT `gateway restart`).

To re-enable, reverse the steps: set `enabled: true`, add the plugin back, restart.

## Pitfalls

- **Don't use `kill -9` on the gateway PID file process** — the PID is already dead, just restart.
- **Don't skip `--replace`** — omitting it produces "already running" error even though the old PID is stale.
- **Don't forget `PYTHONPATH`** when running directly via the venv Python (not using the `hermes` binary wrapper).
- **Gateway logs are append-only** — check the tail, not the head. Use `grep` to find errors rather than `cat`ing the whole file (typical log is 400KB+ over time).
- **`config set` may create duplicate YAML keys** — if you set `gateway.platforms.bale.enabled` but the key path doesn't match the existing structure, it appends a new block instead of editing. After any `config set`, verify with `grep -A2 '<key>' ~/.hermes/config.yaml` that the right value is in the right place.

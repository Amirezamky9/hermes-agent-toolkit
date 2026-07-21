#!/usr/bin/env python3
"""Gateway watchdog: checks every minute. Restarts if gateway dead for 15+ consecutive checks."""
import json, os, subprocess, sys, time
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
GATEWAY_PID_FILE = HERMES_HOME / "gateway.pid"
STAMP_FILE = HERMES_HOME / ".gateway_watchdog_stamp"
CRITICAL_MISSES = 15  # ~15 minutes (1 check per min via cron tick)

def gateway_is_alive():
    if GATEWAY_PID_FILE.exists():
        try:
            pid = json.loads(GATEWAY_PID_FILE.read_text())["pid"]
            os.kill(pid, 0)
            return True
        except (json.JSONDecodeError, KeyError, ProcessLookupError, PermissionError, OSError):
            pass
    result = subprocess.run(
        ["pgrep", "-f", "hermes_cli.*gateway"],
        capture_output=True, text=True, timeout=5
    )
    return result.returncode == 0

alive = gateway_is_alive()
stamp = None
if STAMP_FILE.exists():
    try:
        stamp = int(STAMP_FILE.read_text().strip())
    except (ValueError, OSError):
        pass

now = int(time.time())

if alive:
    # Reset stamp — gateway is fine
    STAMP_FILE.write_text(str(now))
    sys.exit(0)  # silent exit

# Gateway is dead
if stamp is None:
    STAMP_FILE.write_text(str(now))
    sys.exit(0)

missed_seconds = now - stamp
if missed_seconds >= CRITICAL_MISSES * 60:
    print(f"[watchdog] Gateway dead for {missed_seconds}s (>{CRITICAL_MISSES} min). Restarting...")
    subprocess.run(
        ["pkill", "-f", "hermes_cli.*gateway"], timeout=5,
        capture_output=True
    )
    time.sleep(2)
    result = subprocess.run(
        [
            "python3", "-m", "hermes_cli.main", "gateway", "run"
        ],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, "HERMES_HOME": str(HERMES_HOME),
             "PYTHONPATH": str(HERMES_HOME / "hermes-agent")}
    )
    if result.returncode == 0:
        print(f"[watchdog] Gateway restarted successfully")
    else:
        print(f"[watchdog] Restart failed: {result.stderr[:200]}")
    STAMP_FILE.write_text(str(int(time.time())))
else:
    # Dead but not long enough yet — stay silent
    sys.exit(0)

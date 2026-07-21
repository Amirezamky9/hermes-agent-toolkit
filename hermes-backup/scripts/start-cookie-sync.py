#!/usr/bin/env python3
"""Cookie Sync keeper — ensures FastAPI + cloudflared are running."""
import os, subprocess, sys, time
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
WORKDIR = Path("/workspace/hermes-browser-sync")
LOGFILE = HERMES_HOME / "logs" / "cookie-sync.log"
URLFILE = Path("/tmp/cookie-sync-url.txt")
PORT = os.environ.get("PORT", "8000")
API_KEY = os.environ.get("HERMES_API_KEY", "7jJt8VW7OvdbhgMiJ5bVy9BWZOtJHMBBC1p82zIatmQ")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {msg}"
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    with LOGFILE.open("a") as f:
        f.write(entry + "\n")

def find_proc(keyword):
    """Check /proc for matching cmdline (no pgrep available)."""
    for pid_dir in Path("/proc").iterdir():
        if not pid_dir.name.isdigit():
            continue
        cmdline_file = pid_dir / "cmdline"
        if cmdline_file.exists():
            try:
                content = cmdline_file.read_text().replace("\0", " ")
                if keyword in content:
                    return int(pid_dir.name)
            except (OSError, PermissionError):
                pass
    return None

def start_fastapi():
    log("Starting FastAPI on port %s..." % PORT)
    env = os.environ.copy()
    env["PORT"] = PORT
    env["HERMES_API_KEY"] = API_KEY
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", PORT],
        cwd=str(WORKDIR),
        env=env,
        stdout=open(os.devnull, "w"),
        stderr=subprocess.STDOUT,
    )

def start_cloudflared():
    log("Starting cloudflared tunnel...")
    subprocess.Popen(
        [str(Path.home() / ".local" / "bin" / "cloudflared"),
         "tunnel", "--url", "http://localhost:%s" % PORT],
        stderr=open("/tmp/cloudflared_cookie_py.log", "w"),
        stdout=open(os.devnull, "w"),
    )

# --- MAIN ---
fastapi_pid = find_proc("uvicorn.*%s" % PORT)
if fastapi_pid is None:
    start_fastapi()
    time.sleep(8)
    fastapi_pid = find_proc("uvicorn.*%s" % PORT)
    if fastapi_pid:
        log("FastAPI started (PID %s)" % fastapi_pid)

cf_pid = find_proc("cloudflared.*localhost:%s" % PORT)
if cf_pid is None:
    start_cloudflared()
    time.sleep(10)
    # Extract URL
    cf_log = Path("/tmp/cloudflared_cookie_py.log")
    if cf_log.exists():
        import re
        text = cf_log.read_text()
        m = re.search(r"https://[a-z0-9.-]+\.trycloudflare\.com", text)
        if m:
            URLFILE.write_text(m.group(0))
            log("Tunnel URL: %s" % m.group(0))

fastapi_pid = find_proc("uvicorn.*%s" % PORT)
cf_pid = find_proc("cloudflared.*localhost:%s" % PORT)
url = URLFILE.read_text().strip() if URLFILE.exists() else "unknown"

print("[cookie-sync] FastAPI: %s cloudflared: %s URL: %s" % (
    "running" if fastapi_pid else "DEAD",
    "running" if cf_pid else "DEAD",
    url,
))

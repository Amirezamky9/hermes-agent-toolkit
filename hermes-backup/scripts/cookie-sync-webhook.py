#!/usr/bin/env python3
"""Cookie Sync Webhook — receives browser cookies from CacheCat extension,
auto-updates tool credentials for Twitter/X, Reddit, Xueqiu, and more.

Endpoints:
  POST /              — receive cookies (with domain/cookies payload)
  POST /api/browser-sync — same, alias for extension compat
  POST /api/test-connection — connection test from extension
  GET  /health        — health check

Usage:
  COOKIE_SYNC_TOKEN=xxx python3 cookie-sync-webhook.py
"""

import json, os, sys, time, hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

TOKEN = os.environ.get("COOKIE_SYNC_TOKEN", "")
PORT = int(os.environ.get("COOKIE_SYNC_PORT", 9999))
COOKIE_DIR = Path.home() / ".agent-reach" / "cookies"

# ── Tool credential paths ──────────────────────────────────
RDT_CONFIG = Path.home() / ".config" / "rdt-cli" / "credential.json"
TWITTER_ENV = COOKIE_DIR / "twitter.env"
XUEQIU_JSON = COOKIE_DIR / "xueqiu.json"
YOUTUBE_TXT = COOKIE_DIR / "youtube-cookies.txt"  # Netscape format for yt-dlp
HERMES_COOKIES = COOKIE_DIR / "hermes-cookies.json"  # master merge file


class Handler(BaseHTTPRequestHandler):

    def _auth(self) -> bool:
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer ") and auth[7:] == TOKEN:
            return True
        if self.path.strip("/") == TOKEN:
            return True
        return False

    # ── POST ───────────────────────────────────────────────
    def do_POST(self):
        if not self._auth():
            return self._json(401, {"error": "Unauthorized"})

        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
        except Exception:
            return self._json(400, {"error": "Invalid JSON"})

        # connection_test (extension test button)
        if data.get("type") == "connection_test":
            return self._json(200, {
                "success": True,
                "message": "Connection successful",
                "timestamp": data.get("timestamp", ""),
            })

        domain = data.get("domain", "")
        cookies = data.get("cookies", [])
        if not domain or not cookies:
            return self._json(400, {"error": "Missing domain or cookies"})

        COOKIE_DIR.mkdir(parents=True, exist_ok=True)

        # save raw payload per domain
        safe = domain.strip(".").replace(".", "_")
        (COOKIE_DIR / f"{safe}.json").write_text(
            json.dumps(data, indent=2, default=str)
        )

        # merge into master cookie store
        self._merge_cookies(domain, cookies)

        # tool-specific credential updates
        self._update_tools(domain.lower(), cookies)

        self._json(200, {"success": True, "domain": domain, "count": len(cookies)})

    # ── GET ────────────────────────────────────────────────
    def do_GET(self):
        if self.path == "/health":
            return self._json(200, {"status": "ok", "uptime": time.time()})
        self.send_error(404)

    # ── helpers ────────────────────────────────────────────
    def _json(self, code: int, body: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")

    # ── merge cookies into master store ────────────────────
    def _merge_cookies(self, domain: str, cookies: list):
        """Merge incoming cookies into hermes-cookies.json (dedup by name+domain)."""
        store = {}
        if HERMES_COOKIES.exists():
            try:
                store = json.loads(HERMES_COOKIES.read_text())
            except Exception:
                store = {}

        for c in cookies:
            key = f"{c['name']}|{c.get('domain', domain)}"
            store[key] = {
                "name": c["name"],
                "value": c["value"],
                "domain": c.get("domain", domain),
                "path": c.get("path", "/"),
                "secure": c.get("secure", False),
                "httpOnly": c.get("httpOnly", False),
                "sameSite": c.get("sameSite", "None"),
                "expirationDate": c.get("expirationDate"),
                "session": c.get("session", True),
                "updated_at": datetime.now().isoformat(),
            }

        HERMES_COOKIES.write_text(json.dumps(store, indent=2))
        print(f"  → merged {len(cookies)} cookies into master store ({len(store)} total)")

    # ── tool-specific updates ──────────────────────────────
    def _update_tools(self, domain: str, cookies: list):
        cm = {c["name"]: c["value"] for c in cookies}

        if "twitter" in domain or "x.com" in domain:
            self._update_twitter(cm)
        if "reddit" in domain:
            self._update_reddit(cookies)
        if "xueqiu" in domain:
            self._update_xueqiu(cm)
        if "youtube" in domain:
            self._update_youtube(cookies)

    def _update_twitter(self, cm: dict):
        auth_token = cm.get("auth_token", "")
        ct0 = cm.get("ct0", "")
        if auth_token:
            TWITTER_ENV.parent.mkdir(parents=True, exist_ok=True)
            TWITTER_ENV.write_text(
                f"export TWITTER_AUTH_TOKEN={auth_token}\n"
                f"export TWITTER_CT0={ct0}\n"
            )
            print(f"  → twitter-cli: auth_token={len(auth_token)}c, ct0={len(ct0)}c")

    def _update_reddit(self, cookies: list):
        session_cookie = next((c for c in cookies if c["name"] == "reddit_session"), None)
        if session_cookie:
            RDT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
            cred = {
                "cookies": {"reddit_session": session_cookie["value"]},
                "source": "webhook",
                "username": "",
                "modhash": None,
                "saved_at": int(time.time()),
                "last_verified_at": None,
            }
            RDT_CONFIG.write_text(json.dumps(cred, indent=2))
            print(f"  → rdt-cli: credential.json updated")

    def _update_xueqiu(self, cm: dict):
        if cm:
            XUEQIU_JSON.parent.mkdir(parents=True, exist_ok=True)
            XUEQIU_JSON.write_text(json.dumps(cm, indent=2))
            print(f"  → xueqiu: {len(cm)} cookies saved")

    def _update_youtube(self, cookies: list):
        """Write Netscape format cookies.txt for yt-dlp --cookies."""
        lines = ["# Netscape HTTP Cookie File", "# Generated by cookie-sync-webhook", ""]
        for c in cookies:
            domain = c.get("domain", "")
            # Netscape format: domain  tailmatch  path  secure  expiry  name  value
            tailmatch = "TRUE" if domain.startswith(".") else "FALSE"
            path = c.get("path", "/")
            secure = "TRUE" if c.get("secure", False) else "FALSE"
            expiry = int(c.get("expirationDate", 0)) if c.get("expirationDate") else 0
            name = c.get("name", "")
            value = c.get("value", "")
            lines.append(f"{domain}\t{tailmatch}\t{path}\t{secure}\t{expiry}\t{name}\t{value}")
        YOUTUBE_TXT.parent.mkdir(parents=True, exist_ok=True)
        YOUTUBE_TXT.write_text("\n".join(lines) + "\n")
        print(f"  → youtube: {len(cookies)} cookies → {YOUTUBE_TXT}")


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: Set COOKIE_SYNC_TOKEN environment variable")
        sys.exit(1)
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Cookie Sync Webhook listening on :{PORT}")
    print(f"  Token: {TOKEN[:8]}...{TOKEN[-4:]}")
    print(f"  Store: {COOKIE_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
        server.server_close()

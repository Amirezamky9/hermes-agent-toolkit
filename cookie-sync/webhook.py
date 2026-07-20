#!/usr/bin/env python3
"""
Cookie Sync Webhook Server

Receives browser cookies from CacheCat extension and auto-updates
tool credentials for Twitter/X, Reddit, YouTube, and more.

Based on CacheCat project: https://github.com/chinmay29hub/CacheCat
"""

import json
import os
import sys
import time
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

# Configuration
TOKEN = os.environ.get("COOKIE_SYNC_TOKEN", "")
PORT = int(os.environ.get("COOKIE_SYNC_PORT", 9999))
COOKIE_DIR = Path.home() / ".agent-reach" / "cookies"

# Tool credential paths
RDT_CONFIG = Path.home() / ".config" / "rdt-cli" / "credential.json"
TWITTER_ENV = COOKIE_DIR / "twitter.env"
XUEQIU_JSON = COOKIE_DIR / "xueqiu.json"
YOUTUBE_TXT = COOKIE_DIR / "youtube-cookies.txt"
HERMES_COOKIES = COOKIE_DIR / "hermes-cookies.json"


class Handler(BaseHTTPRequestHandler):
    """HTTP request handler for cookie sync"""

    def _auth(self) -> bool:
        """Check authorization"""
        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer ") and auth[7:] == TOKEN:
            return True
        if self.path.strip("/") == TOKEN:
            return True
        return False

    def _json(self, code: int, data: dict):
        """Send JSON response"""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            return self._json(200, {
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
            })
        self._json(404, {"error": "Not found"})

    def do_POST(self):
        """Handle POST requests"""
        if not self._auth():
            return self._json(401, {"error": "Unauthorized"})

        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length))
        except Exception:
            return self._json(400, {"error": "Invalid JSON"})

        # Connection test
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

        # Save raw payload per domain
        safe = domain.strip(".").replace(".", "_")
        (COOKIE_DIR / f"{safe}.json").write_text(
            json.dumps(data, indent=2, default=str)
        )

        # Merge into master cookie store
        self._merge_cookies(domain, cookies)

        # Tool-specific credential updates
        self._update_tools(domain.lower(), cookies)

        self._json(200, {"success": True, "domain": domain, "count": len(cookies)})

    def _merge_cookies(self, domain: str, cookies: list):
        """Merge cookies into master store"""
        store = {}
        if HERMES_COOKIES.exists():
            try:
                store = json.loads(HERMES_COOKIES.read_text())
            except Exception:
                pass

        store[domain] = {
            "cookies": cookies,
            "updated": datetime.now().isoformat(),
        }

        HERMES_COOKIES.write_text(json.dumps(store, indent=2, default=str))

    def _update_tools(self, domain: str, cookies: list):
        """Update tool-specific credentials"""
        cookie_dict = {c["name"]: c.get("value", "") for c in cookies}

        # Twitter/X
        if "twitter.com" in domain or "x.com" in domain:
            auth_token = cookie_dict.get("auth_token", "")
            ct0 = cookie_dict.get("ct0", "")
            if auth_token:
                TWITTER_ENV.write_text(
                    f"TWITTER_AUTH_TOKEN={auth_token}\n"
                    f"TWITTER_CT0={ct0}\n"
                )

        # Reddit
        if "reddit.com" in domain:
            session = cookie_dict.get("reddit_session", "")
            if session:
                RDT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
                RDT_CONFIG.write_text(json.dumps({"reddit_session": session}))

        # YouTube (Netscape format for yt-dlp)
        if "youtube.com" in domain:
            lines = ["# Netscape HTTP Cookie File"]
            for c in cookies:
                domain_val = c.get("domain", domain)
                flag = "TRUE" if domain_val.startswith(".") else "FALSE"
                path = c.get("path", "/")
                secure = "TRUE" if c.get("secure", False) else "FALSE"
                expires = str(int(c.get("expires", 0)))
                name = c.get("name", "")
                value = c.get("value", "")
                lines.append(f"{domain_val}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}")
            YOUTUBE_TXT.write_text("\n".join(lines))

        # Xueqiu
        if "xueqiu.com" in domain:
            token = cookie_dict.get("xq_a_token", "")
            if token:
                XUEQIU_JSON.write_text(json.dumps({"xq_a_token": token}))

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def main():
    if not TOKEN:
        print("ERROR: Set COOKIE_SYNC_TOKEN environment variable")
        print("Generate: export COOKIE_SYNC_TOKEN=$(python3 -c \"import secrets; print(secrets.token_urlsafe(32))\")")
        sys.exit(1)

    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Cookie Sync Server running on http://0.0.0.0:{PORT}")
    print(f"Health check: http://localhost:{PORT}/health")
    print(f"Token: {TOKEN[:8]}...")
    print("Press Ctrl+C to stop")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()

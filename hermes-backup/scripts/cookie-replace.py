#!/usr/bin/env python3
"""cookie-replace.py — Replace cookies in tool config files from master store.

Reads ~/.agent-reach/cookies/hermes-cookies.json (populated by webhook)
and writes them into tool-specific config files.

Usage:
  python3 cookie-replace.py                    # update all tools
  python3 cookie-replace.py --domain x.com     # update only twitter
  python3 cookie-replace.py --domain reddit.com # update only reddit
  python3 cookie-replace.py --list             # show what's stored
  python3 cookie-replace.py --from-file X.json # import from JSON file
"""

import json, os, sys, time, argparse
from pathlib import Path
from datetime import datetime

COOKIE_DIR = Path.home() / ".agent-reach" / "cookies"
HERMES_COOKIES = COOKIE_DIR / "hermes-cookies.json"

# ── Tool config paths ──────────────────────────────────────
RDT_CONFIG = Path.home() / ".config" / "rdt-cli" / "credential.json"
TWITTER_ENV = COOKIE_DIR / "twitter.env"
XUEQIU_JSON = COOKIE_DIR / "xueqiu.json"


def load_master_store() -> dict:
    if not HERMES_COOKIES.exists():
        return {}
    return json.loads(HERMES_COOKIES.read_text())


def save_master_store(store: dict):
    COOKIE_DIR.mkdir(parents=True, exist_ok=True)
    HERMES_COOKIES.write_text(json.dumps(store, indent=2))


def import_from_file(filepath: str) -> dict:
    """Import cookies from a JSON file (CacheCat format or raw cookie list)."""
    data = json.loads(Path(filepath).read_text())

    # handle CacheCat format: {domain, cookies: [...], timestamp}
    if "cookies" in data and "domain" in data:
        cookies = data["cookies"]
        domain = data["domain"]
    elif isinstance(data, list):
        cookies = data
        domain = "unknown"
    else:
        print(f"ERROR: unrecognized format in {filepath}")
        return {}

    store = load_master_store()
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

    save_master_store(store)
    print(f"Imported {len(cookies)} cookies from {filepath}")
    return store


def list_cookies(store: dict):
    """Print stored cookies grouped by domain."""
    by_domain = {}
    for key, c in store.items():
        d = c["domain"]
        if d not in by_domain:
            by_domain[d] = []
        by_domain[d].append(c)

    for domain, cookies in sorted(by_domain.items()):
        print(f"\n[{domain}] ({len(cookies)} cookies)")
        for c in cookies:
            exp = "session" if c.get("session") else (
                f"exp={c.get('expirationDate', '?')}"
            )
            print(f"  {c['name']:30s} {c['value'][:20]:20s} {exp}")


# ── Tool updaters ──────────────────────────────────────────
def update_twitter(store: dict) -> bool:
    """Write twitter-cli env file from auth_token + ct0 cookies."""
    auth = ct0 = ""
    for key, c in store.items():
        if "x.com" in c["domain"] or "twitter" in c["domain"]:
            if c["name"] == "auth_token":
                auth = c["value"]
            elif c["name"] == "ct0":
                ct0 = c["value"]

    if not auth:
        return False

    TWITTER_ENV.parent.mkdir(parents=True, exist_ok=True)
    TWITTER_ENV.write_text(f"export TWITTER_AUTH_TOKEN={auth}\nexport TWITTER_CT0={ct0}\n")
    print(f"  [twitter] auth_token={len(auth)}c, ct0={len(ct0)}c")
    return True


def update_reddit(store: dict) -> bool:
    """Write rdt-cli credential.json from reddit_session cookie."""
    session = ""
    for key, c in store.items():
        if "reddit" in c["domain"] and c["name"] == "reddit_session":
            session = c["value"]

    if not session:
        return False

    RDT_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    cred = {
        "cookies": {"reddit_session": session},
        "source": "webhook",
        "username": "",
        "modhash": None,
        "saved_at": int(time.time()),
        "last_verified_at": None,
    }
    RDT_CONFIG.write_text(json.dumps(cred, indent=2))
    print(f"  [reddit] credential.json updated")
    return True


def update_xueqiu(store: dict) -> bool:
    """Write xueqiu cookie file."""
    xq = {}
    for key, c in store.items():
        if "xueqiu" in c["domain"]:
            xq[c["name"]] = c["value"]

    if not xq:
        return False

    XUEQIU_JSON.parent.mkdir(parents=True, exist_ok=True)
    XUEQIU_JSON.write_text(json.dumps(xq, indent=2))
    print(f"  [xueqiu] {len(xq)} cookies saved")
    return True


DOMAIN_MAP = {
    "x.com": update_twitter,
    "twitter.com": update_twitter,
    "reddit.com": update_reddit,
    "xueqiu.com": update_xueqiu,
}


def main():
    parser = argparse.ArgumentParser(description="Replace cookies in tool configs")
    parser.add_argument("--domain", help="Only update tools for this domain")
    parser.add_argument("--from-file", help="Import cookies from JSON file first")
    parser.add_argument("--list", action="store_true", help="List stored cookies")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated")
    args = parser.parse_args()

    if args.from_file:
        import_from_file(args.from_file)

    store = load_master_store()

    if not store:
        print("No cookies stored. Send some via the webhook first.")
        return

    if args.list:
        list_cookies(store)
        return

    print(f"Updating tools from {len(store)} stored cookies...")

    if args.domain:
        updater = DOMAIN_MAP.get(args.domain)
        if updater:
            if not args.dry_run:
                updater(store)
            else:
                print(f"  [dry-run] would update {args.domain}")
        else:
            print(f"  No tool updater for domain: {args.domain}")
    else:
        for name, updater in DOMAIN_MAP.items():
            if not args.dry_run:
                updater(store)
            else:
                print(f"  [dry-run] would check {name}")


if __name__ == "__main__":
    main()

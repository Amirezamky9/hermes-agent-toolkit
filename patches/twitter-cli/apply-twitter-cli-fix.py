#!/usr/bin/env python3
"""
Apply the twitter-cli ClientTransaction fix.
Run after every `pip install --upgrade twitter-cli` to patch the broken URL.

Usage:
    python3 apply-twitter-cli-fix.py
    python3 apply-twitter-cli-fix.py --check     # dry-run, report status
"""

import os, sys, re

PATCH_FILE = os.path.join(os.path.dirname(__file__), "fix-search-clienttransaction.patch")

CLIENT_PY = None
for site in [
    os.path.expanduser("~/.local/lib/python3.12/site-packages"),
    "/usr/local/lib/python3.12/site-packages",
    "/usr/lib/python3.12/site-packages",
]:
    p = os.path.join(site, "twitter_cli", "client.py")
    if os.path.exists(p):
        CLIENT_PY = p
        break

if not CLIENT_PY:
    print("❌ twitter-cli client.py not found")
    sys.exit(1)

with open(CLIENT_PY) as f:
    content = f.read()

OLD = '"https://x.com"'
NEW = '"https://x.com/home"'

if OLD in content:
    if "--check" in sys.argv:
        print("⚠️  twitter-cli needs patching (x.com → x.com/home)")
        sys.exit(0)
    content = content.replace(OLD, NEW, 1)
    with open(CLIENT_PY, "w") as f:
        f.write(content)
    print(f"✅ Patched {CLIENT_PY}")
elif NEW in content:
    print("✅ twitter-cli already patched")
else:
    print("❌ Unexpected client.py content — manual check needed")
    sys.exit(1)

"""
config.py  –  Central configuration for TelegramTools  (optional)
------------------------------------------------------------------
When present, every module imports this for credentials and settings.
When absent, each module falls back to its own inline resolver.
"""

import os
import sys
import getpass
from pathlib import Path


# ---------------------------------------------------------------------------
# Credential resolution: .env → env vars → interactive prompt
# ---------------------------------------------------------------------------

def _load_dotenv(path):
    vals = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                vals[key.strip()] = val.strip().strip('"').strip("'")
    except OSError:
        pass
    return vals


def _resolve_credentials():
    api_id = api_hash = None
    session = "telegram"

    # 0. config.yaml — telegram-toolkit
    _here = Path(__file__).resolve().parent.parent  # telegram-toolkit/
    config_yaml = _here / "config.yaml"
    if config_yaml.is_file():
        try:
            import yaml
            with open(config_yaml) as f:
                cfg = yaml.safe_load(f)
            api_id = cfg.get("api_id") or api_id
            api_hash = cfg.get("api_hash") or api_hash
            if api_id and api_hash:
                return int(api_id), api_hash, session
        except Exception:
            pass

    # 1. telegram.env — agent-reach
    env_file = Path.home() / ".agent-reach/cookies/telegram.env"
    if env_file.is_file():
        d = _load_dotenv(env_file)
        api_id = d.get("TG_API_ID") or api_id
        api_hash = d.get("TG_API_HASH") or api_hash
        if api_id and api_hash:
            return int(api_id), api_hash, session

    # 2. .env — project root, home dir, cwd
    for p in dict.fromkeys([_here / ".env", Path.home() / ".env", Path.cwd() / ".env"]):
        if p.is_file():
            d = _load_dotenv(p)
            api_id   = d.get("API_ID")   or d.get("TG_API_ID") or api_id
            api_hash = d.get("API_HASH") or d.get("TG_API_HASH") or api_hash
            session  = d.get("SESSION_NAME", session)
            if api_id and api_hash:
                return int(api_id), api_hash, session

    # 3. Environment variables
    api_id   = os.getenv("TG_API_ID") or os.getenv("API_ID") or api_id
    api_hash = os.getenv("TG_API_HASH") or os.getenv("API_HASH") or api_hash
    if api_id and api_hash:
        return int(api_id), api_hash, session

    # 4. Interactive prompt (last resort)
    print("\n[!] Telegram API credentials not found.")
    print("    Get yours at https://my.telegram.org/apps\n")
    while not api_id:
        raw = input("    API_ID  (numeric): ").strip()
        if raw.isdigit():
            api_id = raw
        else:
            print("    API_ID must be a number — please try again.")
    while not api_hash:
        raw = getpass.getpass("    API_HASH (hidden): ").strip()
        if raw:
            api_hash = raw
        else:
            print("    API_HASH cannot be empty — please try again.")

    return int(api_id), api_hash, session


API_ID, API_HASH, SESSION_NAME = _resolve_credentials()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR   = "data"
GROUP_FILE = os.path.join(DATA_DIR, "groups.txt")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# ---------------------------------------------------------------------------
# Scraping defaults
# ---------------------------------------------------------------------------
DEFAULT_KEYWORD  = ""
DEFAULT_LIMIT    = 1000
REPLY_ITER_LIMIT = 500

# ---------------------------------------------------------------------------
# Output verbosity
# ---------------------------------------------------------------------------
VERBOSE  = True
INFO     = True
SUCCESS  = True
WARNING  = False
ERROR    = False
PROGRESS = True

# ---------------------------------------------------------------------------
# Module discovery filters  (main.py)
# ---------------------------------------------------------------------------
DISCOVER_IGNORE = ['!']
WEB_IGNORE      = ['#']

# ---------------------------------------------------------------------------
# Output path regex patterns  (main.py)
# ---------------------------------------------------------------------------
FILE_PATH_PATTERNS = [
    r'[Ss]aved to\s+([\w\-/\\:. ]+)',
    r'[Ee]xported to\s+([\w\-/\\:. ]+)',
    r'[Rr]esults for this group are in\s+([\w\-/\\:. ]+)',
    r'[Oo]utput(?:\s+path)?[:\s]+([\w\-/\\:. ]+)',
    r'[Pp]rocessing group[:\s]+([\w\-/\\:. ]+)',
    r'[Cc]ollecting (?:infrastructure|data) for[:\s]+([\w\-/\\:. ]+)',
]

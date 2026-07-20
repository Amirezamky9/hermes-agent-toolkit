#!/usr/bin/env bash
# research-telegram.sh — تحقیق از Telegram با Telethon
# Usage: research-telegram.sh "query" [channel] [limit]
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

QUERY="${1:-}"
CHANNEL="${2:-}"
LIMIT="${3:-10}"

if [ -z "$QUERY" ]; then
    echo "Usage: research-telegram.sh \"query\" [channel] [limit]"
    echo "  channel: @username or empty for global search"
    exit 1
fi

# Use toolkit CLI
TOOLKIT="$HOME/.agent-reach/tools/telegram-toolkit"
if [ -f "$TOOLKIT/cli.py" ]; then
    if [ -n "$CHANNEL" ]; then
        python3 "$TOOLKIT/cli.py" search "$QUERY" --channel "$CHANNEL" --limit "$LIMIT" --format ai
    else
        python3 "$TOOLKIT/cli.py" search "$QUERY" --limit "$LIMIT" --format ai
    fi
else
    # Fallback to inline Python
    cat > /tmp/tg_search.py << PYEOF
import asyncio, os, sys

async def main():
    from telethon import TelegramClient
    
    api_id = int(os.environ.get("TG_API_ID", "0"))
    api_hash = os.environ.get("TG_API_HASH", "")
    
    if not api_id or not api_hash:
        print("❌ TG_API_ID and TG_API_HASH required")
        sys.exit(1)
    
    session = os.path.expanduser("~/.agent-reach/tools/telegram-toolkit/telegram.session")
    client = TelegramClient(session, api_id, api_hash)
    await client.start()
    
    query = "$QUERY"
    channel = "$CHANNEL" or None
    limit = int("$LIMIT")
    
    results = []
    async for msg in client.iter_messages(channel, search=query, limit=limit):
        chat = await msg.get_chat()
        results.append({
            "id": msg.id,
            "chat": getattr(chat, 'title', 'Unknown'),
            "text": (msg.text or "")[:200],
            "date": str(msg.date),
        })
    
    import json
    print(json.dumps({"query": query, "count": len(results), "results": results}, ensure_ascii=False))
    await client.disconnect()

asyncio.run(main())
PYEOF
    
    [ -f ~/.agent-reach/cookies/telegram.env ] && source ~/.agent-reach/cookies/telegram.env
    python3 /tmp/tg_search.py
fi

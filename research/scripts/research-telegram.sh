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

# Create Python script
cat > /tmp/tg_search.py << PYEOF
import asyncio
import os
import sys

async def main():
    from telethon import TelegramClient
    from telethon.tl.functions.messages import SearchGlobalRequest
    
    # Load config
    api_id = int(os.environ.get("TG_API_ID", "0"))
    api_hash = os.environ.get("TG_API_HASH", "")
    
    if not api_id or not api_hash:
        print("❌ TG_API_ID and TG_API_HASH required")
        print("   Set in ~/.agent-reach/cookies/telegram.env")
        sys.exit(1)
    
    session_path = os.path.expanduser("~/.agent-reach/cookies/telegram.session")
    client = TelegramClient(session_path, api_id, api_hash)
    
    await client.start()
    print(f"✅ Connected as: {(await client.get_me()).first_name}")
    
    query = "$QUERY"
    channel = "$CHANNEL" or None
    limit = int("$LIMIT")
    
    print(f"\n=== Search: {query} (limit: {limit}) ===")
    
    count = 0
    async for message in client.iter_messages(
        channel,
        search=query,
        limit=limit
    ):
        count += 1
        sender = await message.get_sender()
        sender_name = getattr(sender, 'first_name', 'Unknown') if sender else 'Channel'
        
        chat = await message.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        
        print(f"\n[{count}] {chat_name}")
        print(f"    From: {sender_name}")
        print(f"    Date: {message.date}")
        print(f"    Views: {message.views or 'N/A'}")
        
        text = message.text or ""
        if len(text) > 200:
            text = text[:200] + "..."
        print(f"    Text: {text}")
        
        if message.media:
            print(f"    Media: {type(message.media).__name__}")
    
    if count == 0:
        print("No results found")
    
    await client.disconnect()

asyncio.run(main())
PYEOF

# Load env if exists
[ -f ~/.agent-reach/cookies/telegram.env ] && source ~/.agent-reach/cookies/telegram.env

python3 /tmp/tg_search.py

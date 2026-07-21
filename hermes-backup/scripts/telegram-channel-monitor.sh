#!/usr/bin/env bash
# telegram-channel-monitor.sh — مانیتور کانال Telegram
# Usage: telegram-channel-monitor.sh <channel> [interval_seconds]
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

CHANNEL="${1:-}"
INTERVAL="${2:-60}"

if [ -z "$CHANNEL" ]; then
    echo "Usage: telegram-channel-monitor.sh <channel> [interval_seconds]"
    exit 1
fi

cat > /tmp/tg_monitor.py << PYEOF
import asyncio
import os
import sys
import json
from datetime import datetime

async def main():
    from telethon import TelegramClient
    
    api_id = int(os.environ.get("TG_API_ID", "0"))
    api_hash = os.environ.get("TG_API_HASH", "")
    
    if not api_id or not api_hash:
        print("❌ TG_API_ID and TG_API_HASH required")
        sys.exit(1)
    
    session_path = os.path.expanduser("~/.agent-reach/cookies/telegram.session")
    client = TelegramClient(session_path, api_id, api_hash)
    await client.start()
    
    channel = "$CHANNEL"
    interval = int("$INTERVAL")
    
    entity = await client.get_entity(channel)
    channel_name = getattr(entity, 'title', channel)
    print(f"👁 Monitoring: {channel_name}")
    print(f"⏱ Interval: {interval}s")
    print("Press Ctrl+C to stop\n")
    
    # Track last seen message
    state_file = os.path.expanduser(f"~/.agent-reach/cookies/monitor_{channel.replace('@','')}.json")
    last_id = 0
    if os.path.exists(state_file):
        with open(state_file) as f:
            last_id = json.load(f).get("last_id", 0)
    
    try:
        while True:
            async for message in client.iter_messages(entity, limit=5):
                if message.id <= last_id:
                    break
                
                sender = await message.get_sender()
                sender_name = getattr(sender, 'first_name', 'Channel') if sender else 'Channel'
                
                print(f"[{message.date}] New message #{message.id}")
                print(f"  From: {sender_name}")
                
                text = (message.text or "")[:200]
                if text:
                    print(f"  Text: {text}")
                
                if message.media:
                    print(f"  Media: {type(message.media).__name__}")
                
                print()
                last_id = max(last_id, message.id)
            
            # Save state
            with open(state_file, 'w') as f:
                json.dump({"last_id": last_id, "updated": datetime.now().isoformat()}, f)
            
            await asyncio.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    
    await client.disconnect()

asyncio.run(main())
PYEOF

[ -f ~/.agent-reach/cookies/telegram.env ] && source ~/.agent-reach/cookies/telegram.env
python3 /tmp/tg_monitor.py

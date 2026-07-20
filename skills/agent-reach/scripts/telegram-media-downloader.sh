#!/usr/bin/env bash
# telegram-media-downloader.sh — دانلود مدیا از کانال/گروه Telegram
# Usage: telegram-media-downloader.sh <channel> [limit] [type]
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"

CHANNEL="${1:-}"
LIMIT="${2:-50}"
MEDIA_TYPE="${3:-all}"

if [ -z "$CHANNEL" ]; then
    echo "Usage: telegram-media-downloader.sh <channel> [limit] [type]"
    echo "  type: photo, video, document, audio, all"
    exit 1
fi

cat > /tmp/tg_download.py << PYEOF
import asyncio
import os
import sys

async def main():
    from telethon import TelegramClient
    from telethon.tl.types import (
        MessageMediaPhoto, MessageMediaDocument,
        DocumentAttributeVideo, DocumentAttributeAudio
    )

    api_id = int(os.environ.get("TG_API_ID", "0"))
    api_hash = os.environ.get("TG_API_HASH", "")

    if not api_id or not api_hash:
        print("❌ TG_API_ID and TG_API_HASH required")
        sys.exit(1)

    session_path = os.path.expanduser("~/.agent-reach/cookies/telegram.session")
    client = TelegramClient(session_path, api_id, api_hash)
    await client.start()

    channel = "$CHANNEL"
    limit = int("$LIMIT")
    media_type = "$MEDIA_TYPE"

    entity = await client.get_entity(channel)
    print(f"✅ Channel: {getattr(entity, 'title', channel)}")

    out_dir = os.path.expanduser(f"~/telegram-media/{channel.replace('@','').replace('/','_')}")
    os.makedirs(out_dir, exist_ok=True)
    print(f"📁 Output: {out_dir}")

    downloaded = 0
    skipped = 0

    async for message in client.iter_messages(entity, limit=limit):
        if not message.media:
            continue

        if media_type != "all":
            if media_type == "photo" and not isinstance(message.media, MessageMediaPhoto):
                skipped += 1
                continue
            if media_type in ("video", "document") and not isinstance(message.media, MessageMediaDocument):
                skipped += 1
                continue
            if media_type == "audio":
                if not isinstance(message.media, MessageMediaDocument):
                    skipped += 1
                    continue
                doc = message.media.document
                has_audio = any(isinstance(a, DocumentAttributeAudio) for a in doc.attributes)
                if not has_audio:
                    skipped += 1
                    continue

        try:
            filename = await client.download_media(message, file=out_dir)
            if filename:
                downloaded += 1
                size = os.path.getsize(filename) / 1024
                print(f"  ✅ [{downloaded}] {os.path.basename(filename)} ({size:.1f} KB)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            skipped += 1

    print(f"\n📊 Summary: {downloaded} downloaded, {skipped} skipped")
    await client.disconnect()

asyncio.run(main())
PYEOF

[ -f ~/.agent-reach/cookies/telegram.env ] && source ~/.agent-reach/cookies/telegram.env
python3 /tmp/tg_download.py

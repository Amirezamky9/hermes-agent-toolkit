#!/usr/bin/env python3
"""
TG Toolkit CLI — خط فرمان یکپارچه Telegram
استفاده: python cli.py <command> [options]
"""

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path

TOOLKIT_DIR = Path(__file__).parent
CONFIG_FILE = TOOLKIT_DIR / "config.yaml"
SESSION_FILE = TOOLKIT_DIR / "telegram.session"


def load_config():
    """Load config from yaml"""
    import yaml
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def load_env():
    """Load API keys from telegram.env"""
    env_file = Path.home() / ".agent-reach/cookies/telegram.env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key] = val
    return {
        "api_id": int(os.environ.get("TG_API_ID", "0")),
        "api_hash": os.environ.get("TG_API_HASH", ""),
    }


async def cmd_search(args):
    """جستجوی پیام"""
    from telethon import TelegramClient
    from telethon.tl.types import Channel, User
    
    env = load_env()
    client = TelegramClient(str(SESSION_FILE), env["api_id"], env["api_hash"])
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}")
    
    channel = args.channel if args.channel != "global" else None
    
    print(f"\n🔍 Searching: {args.query}")
    if channel:
        print(f"   Channel: {channel}")
    print(f"   Limit: {args.limit}\n")
    
    results = []
    async for msg in client.iter_messages(channel, search=args.query, limit=args.limit):
        chat = await msg.get_chat()
        chat_name = getattr(chat, 'title', getattr(chat, 'first_name', 'Unknown'))
        sender = await msg.get_sender()
        sender_name = getattr(sender, 'first_name', 'Unknown') if sender else 'Channel'
        
        result = {
            "id": msg.id,
            "chat": chat_name,
            "sender": sender_name,
            "date": str(msg.date),
            "text": (msg.text or "")[:500],
            "views": msg.views,
            "media": type(msg.media).__name__ if msg.media else None,
        }
        results.append(result)
        
        # Compact output
        text_preview = (msg.text or "")[:80].replace("\n", " ")
        print(f"[{msg.id}] {chat_name} | {sender_name}")
        print(f"    {text_preview}...")
        print()
    
    # Save JSON if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved {len(results)} results to {args.output}")
    
    # AI-friendly output
    if args.format == "ai":
        ai_output = {
            "query": args.query,
            "channel": channel or "global",
            "count": len(results),
            "results": [{"id": r["id"], "chat": r["chat"], "text": r["text"][:200]} for r in results],
        }
        print("\n--- AI OUTPUT ---")
        print(json.dumps(ai_output, ensure_ascii=False))
    
    await client.disconnect()


async def cmd_download(args):
    """دانلود مدیا"""
    from telethon import TelegramClient
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
    
    env = load_env()
    client = TelegramClient(str(SESSION_FILE), env["api_id"], env["api_hash"])
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}")
    
    # Resolve channel
    entity = await client.get_entity(args.channel)
    channel_name = getattr(entity, 'title', args.channel)
    print(f"\n📥 Channel: {channel_name}")
    
    # Output directory
    out_dir = Path(args.output or f"~/telegram-downloads/{args.channel.replace('@','')}")
    out_dir = out_dir.expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output: {out_dir}")
    print(f"📊 Limit: {args.limit}")
    print(f"⏱ Delay: {args.delay}s\n")
    
    downloaded = 0
    skipped = 0
    
    async for msg in client.iter_messages(entity, limit=args.limit):
        if not msg.media:
            continue
        
        # Type filter
        if args.type != "all":
            if args.type == "photo" and not isinstance(msg.media, MessageMediaPhoto):
                skipped += 1
                continue
            if args.type == "video" and not isinstance(msg.media, MessageMediaDocument):
                skipped += 1
                continue
        
        try:
            filename = await client.download_media(msg, file=str(out_dir))
            if filename:
                downloaded += 1
                size = os.path.getsize(filename) / (1024 * 1024)
                print(f"  ✅ [{downloaded}] {os.path.basename(filename)} ({size:.1f} MB)")
                
                # Rate limit
                await asyncio.sleep(args.delay)
        except Exception as e:
            print(f"  ❌ Error: {e}")
            skipped += 1
    
    print(f"\n📊 Summary: {downloaded} downloaded, {skipped} skipped")
    await client.disconnect()


async def cmd_monitor(args):
    """مانیتور کانال"""
    from telethon import TelegramClient
    
    env = load_env()
    client = TelegramClient(str(SESSION_FILE), env["api_id"], env["api_hash"])
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}")
    
    entity = await client.get_entity(args.channel)
    channel_name = getattr(entity, 'title', args.channel)
    print(f"\n👁 Monitoring: {channel_name}")
    print(f"⏱ Interval: {args.interval}s")
    print("Press Ctrl+C to stop\n")
    
    # Track last seen
    state_file = TOOLKIT_DIR / f"monitor_{args.channel.replace('@','')}.json"
    last_id = 0
    if state_file.exists():
        with open(state_file) as f:
            last_id = json.load(f).get("last_id", 0)
    
    try:
        while True:
            async for msg in client.iter_messages(entity, limit=5):
                if msg.id <= last_id:
                    break
                
                sender = await msg.get_sender()
                sender_name = getattr(sender, 'first_name', 'Channel') if sender else 'Channel'
                
                print(f"[{msg.date}] New #{msg.id}")
                print(f"  From: {sender_name}")
                
                text = (msg.text or "")[:200]
                if text:
                    print(f"  Text: {text}")
                
                if msg.media:
                    print(f"  Media: {type(msg.media).__name__}")
                print()
                
                last_id = max(last_id, msg.id)
            
            # Save state
            with open(state_file, "w") as f:
                json.dump({"last_id": last_id}, f)
            
            await asyncio.sleep(args.interval)
    
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    
    await client.disconnect()


async def cmd_export(args):
    """خروجی گرفتن"""
    from telethon import TelegramClient
    
    env = load_env()
    client = TelegramClient(str(SESSION_FILE), env["api_id"], env["api_hash"])
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}")
    
    entity = await client.get_entity(args.channel)
    channel_name = getattr(entity, 'title', args.channel)
    print(f"\n📤 Exporting: {channel_name}")
    print(f"📊 Limit: {args.limit}")
    print(f"📁 Format: {args.format}\n")
    
    messages = []
    async for msg in client.iter_messages(entity, limit=args.limit):
        chat = await msg.get_chat()
        sender = await msg.get_sender()
        
        message_data = {
            "id": msg.id,
            "date": str(msg.date),
            "text": msg.text or "",
            "views": msg.views,
            "media": type(msg.media).__name__ if msg.media else None,
            "forward": bool(msg.forward),
        }
        
        if sender:
            message_data["sender"] = {
                "id": sender.id,
                "name": getattr(sender, 'first_name', ''),
                "username": getattr(sender, 'username', ''),
            }
        
        messages.append(message_data)
    
    # Save
    out_file = Path(args.output or f"~/telegram-export/{args.channel.replace('@','')}.{args.format}")
    out_file = out_file.expanduser()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    if args.format == "json":
        with open(out_file, "w") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    elif args.format == "csv":
        import csv
        with open(out_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=messages[0].keys())
            writer.writeheader()
            writer.writerows(messages)
    
    print(f"✅ Exported {len(messages)} messages to {out_file}")
    await client.disconnect()


async def cmd_info(args):
    """اطلاعات کانال/کاربر"""
    from telethon import TelegramClient
    
    env = load_env()
    client = TelegramClient(str(SESSION_FILE), env["api_id"], env["api_hash"])
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}\n")
    
    entity = await client.get_entity(args.target)
    
    info = {
        "id": entity.id,
        "type": type(entity).__name__,
    }
    
    if hasattr(entity, 'title'):
        info["title"] = entity.title
    if hasattr(entity, 'first_name'):
        info["first_name"] = entity.first_name
    if hasattr(entity, 'username'):
        info["username"] = entity.username
    if hasattr(entity, 'participant_count'):
        info["members"] = entity.participant_count
    if hasattr(entity, 'about'):
        info["about"] = entity.about
    
    print(json.dumps(info, ensure_ascii=False, indent=2))
    await client.disconnect()


def main():
    parser = argparse.ArgumentParser(description="TG Toolkit CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # search
    p_search = subparsers.add_parser("search", help="Search messages")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--channel", "-c", default="global", help="@channel or 'global'")
    p_search.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    p_search.add_argument("--output", "-o", help="Save JSON to file")
    p_search.add_argument("--format", "-f", choices=["text", "ai"], default="text", help="Output format")
    
    # download
    p_download = subparsers.add_parser("download", help="Download media")
    p_download.add_argument("channel", help="@channel")
    p_download.add_argument("--limit", "-l", type=int, default=100, help="Max files")
    p_download.add_argument("--type", "-t", choices=["photo", "video", "all"], default="all")
    p_download.add_argument("--output", "-o", help="Output directory")
    p_download.add_argument("--delay", "-d", type=float, default=1.0, help="Delay between downloads")
    
    # monitor
    p_monitor = subparsers.add_parser("monitor", help="Monitor channel")
    p_monitor.add_argument("channel", help="@channel")
    p_monitor.add_argument("--interval", "-i", type=int, default=60, help="Check interval (seconds)")
    
    # export
    p_export = subparsers.add_parser("export", help="Export messages")
    p_export.add_argument("channel", help="@channel")
    p_export.add_argument("--limit", "-l", type=int, default=1000, help="Max messages")
    p_export.add_argument("--format", "-f", choices=["json", "csv"], default="json")
    p_export.add_argument("--output", "-o", help="Output file")
    
    # info
    p_info = subparsers.add_parser("info", help="Get channel/user info")
    p_info.add_argument("target", help="@channel or @username")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run async
    commands = {
        "search": cmd_search,
        "download": cmd_download,
        "monitor": cmd_monitor,
        "export": cmd_export,
        "info": cmd_info,
    }
    
    asyncio.run(commands[args.command](args))


if __name__ == "__main__":
    main()

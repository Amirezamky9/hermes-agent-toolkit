#!/usr/bin/env python3
"""
auto_join.py — عضویت خودکار در کانال‌های مورد نیاز بات
"""

import asyncio
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.types import ReplyInlineMarkup
import yaml

TOOLKIT_DIR = Path(__file__).parent
SESSION_FILE = TOOLKIT_DIR / "telegram.session"
CONFIG_FILE = TOOLKIT_DIR / "config.yaml"


async def check_and_join(bot_username: str):
    """بررسی و عضویت در کانال‌های مورد نیاز"""
    config = yaml.safe_load(open(CONFIG_FILE))
    client = TelegramClient(str(SESSION_FILE), config["api_id"], config["api_hash"])
    await client.start()
    
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name}")
    
    # ارسال /start
    await client.send_message(bot_username, "/start")
    await asyncio.sleep(2)
    
    # دریافت پیام‌ها
    messages = await client.get_messages(bot_username, limit=5)
    
    for msg in messages:
        if msg.reply_markup and isinstance(msg.reply_markup, ReplyInlineMarkup):
            buttons = []
            for row in msg.reply_markup.rows:
                for btn in row.buttons:
                    buttons.append(btn)
            
            # بررسی آیا پیام اشتراک هست
            if any('مشترک' in (b.text or '') for b in buttons):
                print(f"\n📋 Subscription required for {bot_username}")
                
                joined = 0
                for btn in buttons:
                    if hasattr(btn, 'url') and btn.url and 't.me/' in btn.url:
                        try:
                            entity = await client.get_entity(btn.url)
                            name = getattr(entity, 'title', 'Unknown')
                            await client(JoinChannelRequest(entity))
                            print(f"  ✅ Joined: {name}")
                            joined += 1
                            await asyncio.sleep(1)
                        except Exception as e:
                            print(f"  ❌ Failed: {e}")
                
                # چک اشتراک
                for btn in buttons:
                    if hasattr(btn, 'data') and btn.data == b'check_unified_sub':
                        await client(GetBotCallbackAnswerRequest(
                            bot_username, msg.id, data=btn.data
                        ))
                        print(f"  ✅ Subscriptions verified")
                        break
                
                return joined
    
    print(f"\n✅ No subscription required for {bot_username}")
    return 0


if __name__ == "__main__":
    import sys
    bot = sys.argv[1] if len(sys.argv) > 1 else "@whatsmusicbot"
    asyncio.run(check_and_join(bot))

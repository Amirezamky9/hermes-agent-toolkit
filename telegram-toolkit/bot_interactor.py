#!/usr/bin/env python3
"""
bot_interactor.py — تعامل با Telegram Bots (دکمه‌ها و inline keyboards)
"""

import asyncio
import json
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.tl.types import (
    ReplyInlineMarkup,
    KeyboardButton,
    KeyboardButtonCallback,
    KeyboardButtonUrl,
    ReplyKeyboardMarkup,
)

TOOLKIT_DIR = Path(__file__).parent
SESSION_FILE = TOOLKIT_DIR / "telegram.session"
CONFIG_FILE = TOOLKIT_DIR / "config.yaml"


def load_config():
    import yaml
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


class BotInteractor:
    """کلاس اصلی برای تعامل با بات‌ها"""
    
    def __init__(self):
        config = load_config()
        self.client = TelegramClient(
            str(SESSION_FILE),
            config["api_id"],
            config["api_hash"]
        )
    
    async def start(self):
        await self.client.start()
        me = await self.client.get_me()
        print(f"✅ Connected as: {me.first_name}")
    
    async def stop(self):
        await self.client.disconnect()
    
    async def send_and_wait(self, bot_username: str, message: str, timeout: int = 10):
        """
        پیام به بات بفرست و منتظر جواب باش
        """
        # ارسال پیام
        await self.client.send_message(bot_username, message)
        
        # صبر برای جواب
        await asyncio.sleep(2)
        
        # دریافت آخرین پیام‌ها
        messages = await self.client.get_messages(bot_username, limit=3)
        
        for msg in messages:
            if msg.reply_markup:
                return {
                    "text": msg.text,
                    "buttons": self._parse_buttons(msg.reply_markup),
                    "message_id": msg.id,
                }
        
        return {"text": messages[0].text if messages else "", "buttons": [], "message_id": messages[0].id if messages else None}
    
    def _parse_buttons(self, markup):
        """پارس دکمه‌ها از reply markup"""
        buttons = []
        
        if isinstance(markup, ReplyInlineMarkup):
            for row in markup.rows:
                for btn in row.buttons:
                    buttons.append({
                        "text": btn.text,
                        "data": btn.data.decode() if hasattr(btn, 'data') and btn.data else None,
                        "type": "inline",
                        "url": btn.url if hasattr(btn, 'url') else None,
                    })
        
        elif isinstance(markup, ReplyKeyboardMarkup):
            for row in markup.rows:
                for btn in row.buttons:
                    buttons.append({
                        "text": btn.text,
                        "type": "keyboard",
                    })
        
        return buttons
    
    async def click_button(self, bot_username: str, message_id: int, button_data: bytes):
        """
        کلیک روی دکمه inline
        """
        await self.client(GetBotCallbackAnswerRequest(
            bot_username,
            message_id,
            data=button_data,
        ))
        
        # صبر برای جواب
        await asyncio.sleep(2)
        
        # دریافت جواب
        messages = await self.client.get_messages(bot_username, limit=1)
        
        if messages and messages[0]:
            return {
                "text": messages[0].text,
                "buttons": self._parse_buttons(messages[0].reply_markup) if messages[0].reply_markup else [],
                "message_id": messages[0].id,
            }
        
        return {"text": "", "buttons": [], "message_id": None}
    
    async def click_button_by_text(self, bot_username: str, message_id: int, button_text: str):
        """
        کلیک روی دکمه با متن
        """
        # دریافت پیام با دکمه‌ها
        messages = await self.client.get_messages(bot_username, ids=message_id)
        
        if not messages or not messages[0] or not messages[0].reply_markup:
            return {"text": "No buttons found", "buttons": [], "message_id": None}
        
        # پیدا کردن دکمه
        for row in messages[0].reply_markup.rows:
            for btn in row.buttons:
                if btn.text == button_text and btn.data:
                    return await self.click_button(bot_username, message_id, btn.data)
        
        return {"text": f"Button '{button_text}' not found", "buttons": [], "message_id": None}
    
    async def list_buttons(self, bot_username: str, message_id: int):
        """
        لیست دکمه‌های یک پیام
        """
        messages = await self.client.get_messages(bot_username, ids=message_id)
        
        if not messages or not messages[0] or not messages[0].reply_markup:
            return []
        
        return self._parse_buttons(messages[0].reply_markup)
    
    async def interactive_session(self, bot_username: str, start_message: str = "/start"):
        """
        جلسه تعاملی با بات
        """
        print(f"\n🤖 Interactive session with {bot_username}")
        print("Type 'quit' to exit, 'buttons' to see current buttons\n")
        
        # شروع
        result = await self.send_and_wait(bot_username, start_message)
        print(f"📱 Bot: {result['text'][:200]}")
        
        if result['buttons']:
            print("\n🔘 Buttons:")
            for i, btn in enumerate(result['buttons']):
                print(f"  [{i+1}] {btn['text']}")
        
        current_message_id = result['message_id']
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                
                if user_input.lower() == 'buttons' and current_message_id:
                    buttons = await self.list_buttons(bot_username, current_message_id)
                    print("\n🔘 Buttons:")
                    for i, btn in enumerate(buttons):
                        print(f"  [{i+1}] {btn['text']}")
                    continue
                
                # اگر عدد باشه، روی دکمه کلیک کن
                if user_input.isdigit() and current_message_id:
                    buttons = await self.list_buttons(bot_username, current_message_id)
                    idx = int(user_input) - 1
                    if 0 <= idx < len(buttons) and buttons[idx].get('data'):
                        result = await self.click_button(
                            bot_username,
                            current_message_id,
                            buttons[idx]['data'].encode()
                        )
                        print(f"📱 Bot: {result['text'][:200]}")
                        current_message_id = result['message_id']
                        
                        if result['buttons']:
                            print("\n🔘 Buttons:")
                            for i, btn in enumerate(result['buttons']):
                                print(f"  [{i+1}] {btn['text']}")
                    else:
                        print("❌ Invalid button number or no data")
                    continue
                
                # ارسال متن
                result = await self.send_and_wait(bot_username, user_input)
                print(f"📱 Bot: {result['text'][:200]}")
                current_message_id = result['message_id']
                
                if result['buttons']:
                    print("\n🔘 Buttons:")
                    for i, btn in enumerate(result['buttons']):
                        print(f"  [{i+1}] {btn['text']}")
            
            except EOFError:
                break
            except KeyboardInterrupt:
                break


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Bot Interactor")
    parser.add_argument("bot", help="@bot_username")
    parser.add_argument("--message", "-m", default="/start", help="Initial message")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    interactor = BotInteractor()
    await interactor.start()
    
    if args.interactive:
        await interactor.interactive_session(args.bot, args.message)
    else:
        result = await interactor.send_and_wait(args.bot, args.message)
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"📱 Bot: {result['text']}")
            if result['buttons']:
                print("\n🔘 Buttons:")
                for i, btn in enumerate(result['buttons']):
                    print(f"  [{i+1}] {btn['text']}")
    
    await interactor.stop()


if __name__ == "__main__":
    asyncio.run(main())

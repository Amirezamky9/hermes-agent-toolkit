#!/usr/bin/env python3
"""
music_bot.py — ماژول مقاوم برای تعامل با @whatsmusicbot
抵抗: timeout, subscription, rate limit, flood wait
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from telethon import TelegramClient
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.tl.types import ReplyInlineMarkup
from telethon.errors import (
    FloodWaitError,
    BotResponseTimeoutError,
    RPCError,
)
import yaml

# ─── Configuration ───────────────────────────────────────────────
TOOLKIT_DIR = Path(__file__).parent
SESSION_FILE = TOOLKIT_DIR / "telegram.session"
CONFIG_FILE = TOOLKIT_DIR / "config.yaml"
BOT_USERNAME = "@whatsmusicbot"

# Rate limits
RATE_LIMIT_DELAY = 2.0      # seconds between requests
FLOOD_WAIT_MULTIPLIER = 1.5 # multiply flood wait time
MAX_RETRIES = 3             # max retries on failure
RETRY_DELAY = 5.0           # seconds between retries
BUTTON_CLICK_TIMEOUT = 15   # seconds to wait for bot response
SEARCH_TIMEOUT = 10         # seconds to wait for search results

# ─── Helpers ─────────────────────────────────────────────────────

def load_config():
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def log(msg, level="INFO"):
    """Simple logging"""
    print(f"[{level}] {msg}", file=sys.stderr)


class MusicBot:
    """کلاس مقاوم برای تعامل با @whatsmusicbot"""
    
    def __init__(self):
        config = load_config()
        self.client = TelegramClient(
            str(SESSION_FILE),
            config["api_id"],
            config["api_hash"]
        )
        self.connected = False
        self.last_request_time = 0
        self._subscription_verified = False
    
    async def connect(self):
        """اتصال به تلگرام"""
        if not self.connected:
            await self.client.start()
            me = await self.client.get_me()
            log(f"Connected as: {me.first_name}")
            self.connected = True
    
    async def disconnect(self):
        """قطع اتصال"""
        if self.connected:
            await self.client.disconnect()
            self.connected = False
    
    async def _rate_limit(self):
        """جلوگیری از rate limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            wait = RATE_LIMIT_DELAY - elapsed
            log(f"Rate limit: waiting {wait:.1f}s")
            await asyncio.sleep(wait)
        self.last_request_time = time.time()
    
    async def _safe_request(self, func, *args, **kwargs):
        """درخواست ایمن با retry"""
        for attempt in range(MAX_RETRIES):
            try:
                await self._rate_limit()
                return await func(*args, **kwargs)
            
            except FloodWaitError as e:
                wait_time = e.seconds * FLOOD_WAIT_MULTIPLIER
                log(f"FloodWait: sleeping {wait_time}s", "WARN")
                await asyncio.sleep(wait_time)
            
            except BotResponseTimeoutError:
                log(f"Bot timeout (attempt {attempt + 1}/{MAX_RETRIES})", "WARN")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
            
            except RPCError as e:
                log(f"RPC error: {e} (attempt {attempt + 1}/{MAX_RETRIES})", "ERROR")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
            
            except Exception as e:
                log(f"Unexpected error: {e}", "ERROR")
                raise
        
        raise Exception(f"Failed after {MAX_RETRIES} retries")
    
    def _parse_buttons(self, markup):
        """پارس دکمه‌ها"""
        buttons = []
        if not isinstance(markup, ReplyInlineMarkup):
            return buttons
        
        for row in markup.rows:
            for btn in row.buttons:
                buttons.append({
                    "text": btn.text,
                    "data": btn.data.decode() if hasattr(btn, 'data') and btn.data else None,
                    "url": btn.url if hasattr(btn, 'url') else None,
                })
        return buttons
    
    async def _check_subscription(self, messages):
        """بررسی و رفع اشتراک"""
        for msg in messages:
            if not msg.reply_markup or not isinstance(msg.reply_markup, ReplyInlineMarkup):
                continue
            
            buttons = self._parse_buttons(msg.reply_markup)
            
            # آیا پیام اشتراک هست؟
            has_sub_button = any('مشترک' in (b.get('text') or '') for b in buttons)
            if not has_sub_button:
                continue
            
            log("Subscription required - joining channels...")
            
            # عضویت در کانال‌ها
            from telethon.tl.functions.channels import JoinChannelRequest
            
            for btn in buttons:
                if btn.get('url') and 't.me/' in btn['url']:
                    try:
                        entity = await self.client.get_entity(btn['url'])
                        name = getattr(entity, 'title', 'Unknown')
                        await self.client(JoinChannelRequest(entity))
                        log(f"Joined: {name}")
                        await asyncio.sleep(1)
                    except Exception as e:
                        log(f"Failed to join: {e}", "WARN")
            
            # چک اشتراک
            for btn in buttons:
                if btn.get('data') == 'check_unified_sub':
                    try:
                        await self.client(GetBotCallbackAnswerRequest(
                            BOT_USERNAME, msg.id, data=btn['data'].encode()
                        ))
                        log("Subscription verified")
                        self._subscription_verified = True
                        await asyncio.sleep(1)
                        return True
                    except Exception as e:
                        log(f"Subscription check failed: {e}", "ERROR")
        
        return False
    
    async def send_message(self, text: str):
        """ارسال پیام به بات"""
        await self.client.send_message(BOT_USERNAME, text)
    
    async def get_latest_messages(self, limit: int = 3):
        """دریافت آخرین پیام‌ها"""
        return await self.client.get_messages(BOT_USERNAME, limit=limit)
    
    async def click_button(self, message_id: int, button_data: str):
        """کلیک روی دکمه"""
        await self.client(GetBotCallbackAnswerRequest(
            BOT_USERNAME, message_id, data=button_data.encode()
        ))
    
    async def download_media(self, message, output_dir: str = "/tmp/"):
        """دانلود فایل صوتی"""
        filename = await self.client.download_media(message, file=output_dir)
        if filename:
            size = os.path.getsize(filename) / (1024 * 1024)
            log(f"Downloaded: {filename} ({size:.1f} MB)")
        return filename
    
    # ─── Public API ──────────────────────────────────────────────
    
    async def search(self, query: str, check_sub: bool = True):
        """
        جستجوی آهنگ
        
        Args:
            query: نام آهنگ یا لینک
            check_sub: بررسی اشتراک
        
        Returns:
            dict: {text, buttons, message_id}
        """
        await self.connect()
        
        # ارسال جستجو
        await self._safe_request(self.send_message, query)
        await asyncio.sleep(SEARCH_TIMEOUT)
        
        # دریافت پیام‌ها
        messages = await self._safe_request(self.get_latest_messages, 5)
        
        # بررسی اشتراک
        if check_sub and not self._subscription_verified:
            await self._check_subscription(messages)
            # دریافت مجدد پیام‌ها بعد از عضویت
            messages = await self._safe_request(self.get_latest_messages, 5)
        
        # پیدا کردن پیام با دکمه‌ها
        for msg in messages:
            if msg.reply_markup and isinstance(msg.reply_markup, ReplyInlineMarkup):
                buttons = self._parse_buttons(msg.reply_markup)
                # فیلتر دکمه‌های track
                track_buttons = [b for b in buttons if b.get('data') and 'track_id' in b['data']]
                if track_buttons:
                    return {
                        "text": msg.text or "",
                        "buttons": track_buttons,
                        "message_id": msg.id,
                    }
        
        return {"text": "", "buttons": [], "message_id": None}
    
    async def select_track(self, message_id: int, button_index: int = 0):
        """
        انتخاب آهنگ از نتایج
        
        Args:
            message_id: شناسه پیام نتایج
            button_index: شماره دکمه (0 = اولین)
        
        Returns:
            dict: {text, buttons, message_id, track_info}
        """
        await self.connect()
        
        # دریافت پیام
        messages = await self._safe_request(self.get_latest_messages, 5)
        target_msg = None
        for msg in messages:
            if msg.id == message_id:
                target_msg = msg
                break
        
        if not target_msg:
            # احتمالاً پیام جدیدتر اومده، آخرین رو بگیر
            target_msg = messages[0] if messages else None
        
        if not target_msg or not target_msg.reply_markup:
            return {"text": "Message not found", "buttons": [], "message_id": None}
        
        buttons = self._parse_buttons(target_msg.reply_markup)
        track_buttons = [b for b in buttons if b.get('data') and 'track_id' in b['data']]
        
        if not track_buttons or button_index >= len(track_buttons):
            return {"text": "No track buttons found", "buttons": [], "message_id": None}
        
        btn = track_buttons[button_index]
        
        # کلیک
        await self._safe_request(self.click_button, target_msg.id, btn['data'])
        await asyncio.sleep(2)
        
        # دریافت جواب
        messages = await self._safe_request(self.get_latest_messages, 3)
        
        for msg in messages:
            if msg.reply_markup and isinstance(msg.reply_markup, ReplyInlineMarkup):
                reply_buttons = self._parse_buttons(msg.reply_markup)
                return {
                    "text": msg.text or "",
                    "buttons": reply_buttons,
                    "message_id": msg.id,
                    "track_info": btn['text'],
                }
        
        return {"text": messages[0].text if messages else "", "buttons": [], "message_id": messages[0].id if messages else None}
    
    async def get_lyrics(self, message_id: int):
        """
        دریافت متن ترانه
        
        Args:
            message_id: شناسه پیام آهنگ
        
        Returns:
            dict: {text, message_id}
        """
        await self.connect()
        
        messages = await self._safe_request(self.get_latest_messages, 5)
        target_msg = None
        for msg in messages:
            if msg.id == message_id:
                target_msg = msg
                break
        
        if not target_msg:
            target_msg = messages[0] if messages else None
        
        if not target_msg or not target_msg.reply_markup:
            return {"text": "Message not found", "message_id": None}
        
        buttons = self._parse_buttons(target_msg.reply_markup)
        
        for btn in buttons:
            if 'متن' in btn.get('text', '') and btn.get('data'):
                await self._safe_request(self.click_button, target_msg.id, btn['data'])
                await asyncio.sleep(2)
                
                messages = await self._safe_request(self.get_latest_messages, 2)
                return {
                    "text": messages[0].text if messages else "",
                    "message_id": messages[0].id if messages else None,
                }
        
        return {"text": "Lyrics button not found", "message_id": None}
    
    async def download_track(self, message_id: int, output_dir: str = "/tmp/"):
        """
        دانلود آهنگ
        
        Args:
            message_id: شناسه پیام آهنگ
            output_dir: پوشه خروجی
        
        Returns:
            dict: {filename, size_mb, message_id}
        """
        await self.connect()
        
        messages = await self._safe_request(self.get_latest_messages, 5)
        target_msg = None
        for msg in messages:
            if msg.id == message_id:
                target_msg = msg
                break
        
        if not target_msg:
            target_msg = messages[0] if messages else None
        
        if not target_msg or not target_msg.media:
            return {"filename": None, "size_mb": 0, "message_id": None}
        
        filename = await self._safe_request(self.download_media, target_msg, output_dir)
        
        if filename:
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            return {
                "filename": filename,
                "size_mb": round(size_mb, 2),
                "message_id": message_id,
            }
        
        return {"filename": None, "size_mb": 0, "message_id": None}
    
    async def full_search(self, query: str, output_dir: str = "/tmp/"):
        """
        جستجوی کامل: جستجو + انتخاب + دانلود
        
        Args:
            query: نام آهنگ
            output_dir: پوشه خروجی
        
        Returns:
            dict: {track_info, filename, size_mb, lyrics}
        """
        log(f"Full search: {query}")
        
        # جستجو
        search_result = await self.search(query)
        if not search_result['buttons']:
            return {"error": "No results found", "track_info": None, "filename": None}
        
        log(f"Found {len(search_result['buttons'])} results")
        
        # انتخاب اولین نتیجه
        select_result = await self.select_track(search_result['message_id'], 0)
        if not select_result.get('track_info'):
            return {"error": "Failed to select track", "track_info": None, "filename": None}
        
        log(f"Selected: {select_result['track_info']}")
        
        # دانلود
        download_result = await self.download_track(select_result['message_id'], output_dir)
        
        # متن ترانه (اختیاری)
        lyrics = ""
        try:
            lyrics_result = await self.get_lyrics(select_result['message_id'])
            lyrics = lyrics_result.get('text', '')
        except Exception:
            pass
        
        return {
            "track_info": select_result['track_info'],
            "filename": download_result.get('filename'),
            "size_mb": download_result.get('size_mb', 0),
            "lyrics": lyrics,
            "search_results": len(search_result['buttons']),
        }


# ─── CLI ─────────────────────────────────────────────────────────

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Music Bot (whatsmusicbot)")
    parser.add_argument("action", choices=["search", "download", "lyrics", "full"])
    parser.add_argument("query", help="Song name or link")
    parser.add_argument("--output", "-o", default="/tmp/", help="Output directory")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    
    args = parser.parse_args()
    
    bot = MusicBot()
    
    try:
        if args.action == "search":
            result = await bot.search(args.query)
        
        elif args.action == "download":
            result = await bot.search(args.query)
            if result['buttons']:
                select = await bot.select_track(result['message_id'], 0)
                if select.get('message_id'):
                    result = await bot.download_track(select['message_id'], args.output)
                else:
                    result = {"error": "Failed to select track"}
            else:
                result = {"error": "No results found"}
        
        elif args.action == "lyrics":
            result = await bot.search(args.query)
            if result['buttons']:
                select = await bot.select_track(result['message_id'], 0)
                if select.get('message_id'):
                    result = await bot.get_lyrics(select['message_id'])
                else:
                    result = {"error": "Failed to select track"}
            else:
                result = {"error": "No results found"}
        
        elif args.action == "full":
            result = await bot.full_search(args.query, args.output)
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            elif 'filename' in result and result['filename']:
                print(f"✅ Downloaded: {result['filename']} ({result.get('size_mb', 0)} MB)")
            elif 'text' in result:
                print(result['text'][:500])
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
    
    finally:
        await bot.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

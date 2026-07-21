"""
Bale platform adapter — WORKING TEMPLATE

Tested and verified against Bale Bot API (July 2026).
Copy this as a starting point for new Telegram-compatible adapters.

Key patterns demonstrated:
- Platform("bale") for dynamic enum members
- MessageEvent with source=SessionSource(...)
- connect(is_reconnect=False) signature
- MessageType.PHOTO / DOCUMENT (not IMAGE / FILE)
- media_urls as list, raw_message not raw_data
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional, Set

import httpx

logger = logging.getLogger(__name__)
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter, MessageEvent, MessageType, SendResult,
)
from gateway.session import SessionSource

BALE_API_BASE = "https://tapi.bale.ai"
_MAX_MSG = 4096


def check_bale_requirements() -> bool:
    return True


class BaleAdapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        # Platform("bale") — NOT Platform.BALE
        super().__init__(config, Platform("bale"))
        self.token = config.token or os.getenv("BALE_BOT_TOKEN", "")
        self._http: Optional[httpx.AsyncClient] = None
        self._offset = 0
        self._running = False
        self._polling_task: Optional[asyncio.Task] = None

    async def _req(self, method: str, data: dict | None = None) -> dict:
        if not self._http:
            self._http = httpx.AsyncClient(timeout=30.0)
        url = f"{BALE_API_BASE}/bot{self.token}/{method}"
        try:
            r = await (self._http.post(url, json=data) if data else self._http.get(url))
            return r.json()
        except Exception as e:
            logger.error("[Bale] %s failed: %s", method, e)
            return {"ok": False, "description": str(e)}

    # is_reconnect is REQUIRED — gateway calls connect(is_reconnect=True)
    async def connect(self, is_reconnect: bool = False) -> bool:
        res = await self._req("getMe")
        if not res.get("ok"):
            logger.error("[Bale] connect failed: %s", res.get("description"))
            return False
        bot = res["result"]
        logger.info("[Bale] connected as @%s", bot.get("username"))
        self._running = True
        self._polling_task = asyncio.create_task(self._poll())
        return True

    async def disconnect(self):
        self._running = False
        if self._polling_task:
            self._polling_task.cancel()
        if self._http:
            await self._http.aclose()

    async def _poll(self):
        while self._running:
            try:
                res = await self._req("getUpdates", {"offset": self._offset, "timeout": 30})
                for upd in res.get("result", []):
                    self._offset = upd["update_id"] + 1
                    if "message" in upd:
                        await self._on_message(upd["message"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning("[Bale] poll error: %s", e)
                await asyncio.sleep(5)

    async def _on_message(self, msg: dict):
        user = msg.get("from", {})
        uid = user.get("id")
        if uid is None or user.get("is_bot"):
            return

        chat_id = str(msg.get("chat", {}).get("id", ""))
        text = msg.get("text", "")
        mid = str(msg.get("message_id", ""))

        # MessageType — PHOTO not IMAGE, DOCUMENT not FILE
        mt = MessageType.TEXT
        if "photo" in msg:
            mt = MessageType.PHOTO
        elif "voice" in msg:
            mt = MessageType.VOICE
        elif "video" in msg:
            mt = MessageType.VIDEO
        elif "document" in msg:
            mt = MessageType.DOCUMENT
        elif "audio" in msg:
            mt = MessageType.AUDIO

        # MessageEvent — source=SessionSource, raw_message, media_urls (list)
        event = MessageEvent(
            message_id=mid,
            text=text,
            message_type=mt,
            raw_message=msg,
            source=SessionSource(
                platform=Platform("bale"),
                chat_id=chat_id,
                user_id=str(uid),
                user_name=user.get("first_name", "") or user.get("username", ""),
            ),
        )

        # media_urls is a LIST, not a single string
        media_file_id = None
        if mt == MessageType.PHOTO:
            media_file_id = (msg.get("photo") or [{}])[-1].get("file_id")
        elif mt == MessageType.VOICE:
            media_file_id = msg.get("voice", {}).get("file_id")
        elif mt == MessageType.DOCUMENT:
            media_file_id = msg.get("document", {}).get("file_id")
        if media_file_id:
            event.media_urls = [media_file_id]

        await self.handle_message(event)

    async def send(self, chat_id: str, text: str, reply_to: str | None = None,
                   parse_mode: str | None = None, **kw) -> SendResult:
        data: dict[str, Any] = {"chat_id": chat_id, "text": text[:_MAX_MSG]}
        if reply_to:
            data["reply_to_message_id"] = int(reply_to)
        if parse_mode:
            data["parse_mode"] = parse_mode
        res = await self._req("sendMessage", data)
        if res.get("ok"):
            return SendResult(success=True, message_id=str(res["result"].get("message_id", "")))
        return SendResult(success=False, error=res.get("description", "send failed"))

    async def send_typing(self, chat_id: str):
        await self._req("sendChatAction", {"chat_id": chat_id, "action": "typing"})

    def get_chat_info(self, chat_id: str) -> dict:
        return {"name": f"Bale {chat_id}", "type": "private", "chat_id": chat_id}


def register(ctx) -> None:
    ctx.register_platform(
        name="bale",
        label="Bale",
        adapter_factory=lambda cfg: BaleAdapter(cfg),
        check_fn=check_bale_requirements,
        required_env=["BALE_BOT_TOKEN"],
        cron_deliver_env_var="BALE_HOME_CHANNEL",
        emoji="📱",
    )

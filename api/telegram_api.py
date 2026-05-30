"""Telegram webhook and command API."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import aiohttp
from fastapi import APIRouter, Depends, Header, HTTPException, Request

from trading_system.agents.boss_agent import BossAgent
from trading_system.config.settings import AppSettings

logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram send-message helper."""

    def __init__(self, token: Optional[str], chat_id: Optional[str]) -> None:
        self.token = token
        self.chat_id = chat_id

    async def send_message(self, text: str, chat_id: Optional[str] = None) -> None:
        """Send message to Telegram chat."""
        if not self.token:
            logger.debug("Telegram token missing; message not sent")
            return
        target_chat = chat_id or self.chat_id
        if not target_chat:
            logger.debug("Telegram chat_id missing; message not sent")
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": target_chat, "text": text}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status >= 400:
                    body = await response.text()
                    logger.warning("Telegram send failed status=%s body=%s", response.status, body)


def create_telegram_router(settings: AppSettings, boss_agent: BossAgent, auth_guard: object) -> APIRouter:
    """Create Telegram router with webhook and local command endpoint."""
    router = APIRouter(prefix="/telegram", tags=["telegram"])
    service = TelegramService(
        token=os.getenv("TELEGRAM_BOT_TOKEN"),
        chat_id=os.getenv("TELEGRAM_CHAT_ID"),
    )

    @router.post("/webhook")
    async def telegram_webhook(
        request: Request,
        x_telegram_bot_api_secret_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        expected_secret = settings.api.telegram_webhook_secret
        if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

        payload = await request.json()
        message = payload.get("message", {}) or payload.get("edited_message", {})
        text = message.get("text", "")
        chat = message.get("chat", {})
        chat_id = str(chat.get("id")) if chat else None
        if not text:
            return {"ok": True, "ignored": "no_text"}

        parsed = await boss_agent.handle_command(text)
        await service.send_message(parsed.response, chat_id=chat_id)
        return {"ok": True, "intent": parsed.intent.model_dump(), "response": parsed.response}

    @router.post("/command")
    async def local_command(payload: Dict[str, str], _auth: None = Depends(auth_guard)) -> Dict[str, Any]:
        """Local endpoint useful for testing Telegram command flow."""
        text = payload.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Missing text")
        parsed = await boss_agent.handle_command(text)
        return {"intent": parsed.intent.model_dump(), "response": parsed.response, "payload": parsed.payload}

    return router

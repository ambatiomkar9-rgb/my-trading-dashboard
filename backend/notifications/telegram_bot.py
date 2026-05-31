"""Telegram inline-button approvals for trade signals and callback polling."""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)
def _normalize_dashboard_url(raw_url: str | None) -> str:
    """Prefer a loopback-safe dashboard URL for local paper-mode tests."""
    url = str(raw_url or "").strip().rstrip("/")
    if not url:
        return "http://127.0.0.1:8000"
    if url.startswith("http://localhost"):
        return url.replace("localhost", "127.0.0.1", 1)
    if url.startswith("https://localhost"):
        return url.replace("localhost", "127.0.0.1", 1)
    return url


def _telegram_config() -> dict[str, str]:
    """Read Telegram and dashboard config from the current environment."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    dashboard_url = _normalize_dashboard_url(os.getenv("DASHBOARD_URL"))
    api_token = os.getenv("DASHBOARD_API_TOKEN", "").strip()
    base = f"https://api.telegram.org/bot{token}" if token else ""
    return {
        "token": token,
        "chat_id": chat_id,
        "dashboard_url": dashboard_url,
        "api_token": api_token,
        "base": base,
    }


async def send_approval_request(signal: dict[str, Any]) -> bool:
    """Send a signal to Telegram with Approve/Reject inline buttons."""
    try:
        cfg = _telegram_config()
        if not cfg["token"] or not cfg["chat_id"]:
            return False

        sid = signal["id"]
        sym = str(signal.get("symbol") or "").upper()
        side = str(signal.get("side") or signal.get("signal_type") or "BUY").upper()
        qty = int(signal.get("quantity") or signal.get("qty") or signal.get("quantity_to_buy") or 0)
        price = float(signal.get("price") or signal.get("signal_price") or 0)
        score = signal.get("score", signal.get("overall_score", 0))
        reason = str(signal.get("reason") or signal.get("approval_reason") or "Technical signal")

        try:
            from backend.brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore
        except ModuleNotFoundError:  # noqa: BLE001
            from brokerage.charges_engine import ChargesEngine, TradeSegment  # type: ignore

        engine = ChargesEngine()
        charges = engine.calculate_charges(TradeSegment.intraday, price, price * 1.05, qty, True)

        text = (
            f"🚨 *{side} SIGNAL — {sym}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Price     : ₹{price:.2f}\n"
            f"📦 Quantity  : {qty}\n"
            f"🎯 Score     : {score}/100\n"
            f"📋 Reason    : {reason}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Charges   : ₹{charges.get('total_charges', 0):.2f}\n"
            f"💵 Est. Net  : ₹{charges.get('net_profit', 0):.2f}\n"
            f"📈 Ratio     : {charges.get('profitability_ratio', 0):.1f}x\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ *Approve within 2 minutes*"
        )

        markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ APPROVE", "callback_data": f"approve_{sid}"},
                    {"text": "❌ REJECT", "callback_data": f"reject_{sid}"},
                ]
            ]
        }

        async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
            resp = await client.post(
                f"{cfg['base']}/sendMessage",
                json={
                    "chat_id": cfg["chat_id"],
                    "text": text,
                    "parse_mode": "Markdown",
                    "reply_markup": markup,
                },
            )
            resp.raise_for_status()
            payload = resp.json()
            return bool(payload.get("ok", False))
    except Exception as exc:  # noqa: BLE001
        logger.error("Telegram send error: %s", exc)
        return False


async def send_message(text: str) -> bool:
    """Send a plain Telegram message."""
    try:
        cfg = _telegram_config()
        if not cfg["token"] or not cfg["chat_id"]:
            return False
        async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
            resp = await client.post(
                f"{cfg['base']}/sendMessage",
                json={"chat_id": cfg["chat_id"], "text": text, "parse_mode": "Markdown"},
            )
            resp.raise_for_status()
            return bool(resp.json().get("ok", False))
    except Exception as exc:  # noqa: BLE001
        logger.error("Telegram message error: %s", exc)
        return False


async def answer_callback(callback_query_id: str, text: str) -> None:
    """Acknowledge a Telegram callback query quickly."""
    try:
        cfg = _telegram_config()
        if not cfg["token"]:
            return
        async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
            await client.post(
                f"{cfg['base']}/answerCallbackQuery",
                json={"callback_query_id": callback_query_id, "text": text},
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Answer callback error: %s", exc)


class TelegramCallbackPoller:
    """Polls Telegram updates and updates dashboard signals on button presses."""

    def __init__(self) -> None:
        self._offset = 0
        self._running = False

    async def start(self) -> None:
        """Run the polling loop."""
        try:
            self._running = True
            logger.info("Telegram callback poller started")
            while self._running:
                await self._poll()
                await asyncio.sleep(2)
        except Exception as exc:  # noqa: BLE001
            logger.error("TelegramCallbackPoller start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the polling loop."""
        try:
            self._running = False
        except Exception as exc:  # noqa: BLE001
            logger.error("TelegramCallbackPoller stop failed: %s", exc)

    def _auth_headers(self) -> dict[str, str]:
        cfg = _telegram_config()
        if cfg["api_token"]:
            return {"Authorization": f"Bearer {cfg['api_token']}"}
        admin_key = os.getenv("ADMIN_API_KEY", "").strip()
        return {"X-Admin-Key": admin_key} if admin_key else {}

    async def _poll(self) -> None:
        """Fetch new Telegram updates and process callback presses."""
        try:
            cfg = _telegram_config()
            if not cfg["token"]:
                return
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                resp = await client.get(
                    f"{cfg['base']}/getUpdates",
                    params={"offset": self._offset, "timeout": 5},
                )
                resp.raise_for_status()
                payload = resp.json()
                if not payload.get("ok"):
                    return
                updates = payload.get("result", [])

            for update in updates:
                self._offset = int(update.get("update_id", self._offset)) + 1
                callback = update.get("callback_query")
                if callback:
                    await self._handle_callback(callback)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Poll error: %s", exc)

    async def _handle_callback(self, callback: dict[str, Any]) -> None:
        """Handle approve/reject button presses."""
        try:
            data = str(callback.get("data") or "")
            callback_id = str(callback.get("id") or "")
            user = callback.get("from", {}).get("first_name", "User")

            if data.startswith("approve_"):
                signal_id = data.split("_", 1)[1]
                await answer_callback(callback_id, "✅ Signal approved!")
                ok = await self._update_signal(signal_id, "approved", "Telegram approved")
                if ok:
                    await send_message(f"✅ *{user} approved signal #{signal_id}*\nExecuting now…")
                else:
                    await send_message(f"⚠️ *{user} approved signal #{signal_id}* but dashboard update failed")
            elif data.startswith("reject_"):
                signal_id = data.split("_", 1)[1]
                await answer_callback(callback_id, "❌ Signal rejected")
                ok = await self._update_signal(signal_id, "rejected", "Telegram rejected")
                if ok:
                    await send_message(f"❌ *{user} rejected signal #{signal_id}*")
                else:
                    await send_message(f"⚠️ *{user} rejected signal #{signal_id}* but dashboard update failed")
        except Exception as exc:  # noqa: BLE001
            logger.error("Callback handling failed: %s", exc)

    async def _update_signal(self, signal_id: str, status: str, reason: str | None = None) -> bool:
        """Patch the dashboard signal status."""
        try:
            if not signal_id:
                return False
            async with httpx.AsyncClient(timeout=10, trust_env=False) as client:
                resp = await client.patch(
                    f"{_telegram_config()['dashboard_url']}/api/signals/{signal_id}",
                    json={"status": status, "reason": reason},
                    headers=self._auth_headers(),
                )
                return resp.status_code == 200
        except Exception as exc:  # noqa: BLE001
            logger.error("Update signal error: %s", exc)
            return False

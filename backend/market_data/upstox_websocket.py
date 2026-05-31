"""Upstox market-data WebSocket wrapper with tick parsing and reconnect support."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Awaitable, Callable

try:
    from backend.execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from backend.market_data.reconnect_manager import ReconnectManager  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from market_data.reconnect_manager import ReconnectManager  # type: ignore

logger = logging.getLogger(__name__)
WS_URL = "wss://api.upstox.com/v2/feed/market-data-feed"


def _parse(raw: bytes | str) -> list[dict[str, Any]]:
    """Parse an Upstox tick frame into normalized tick dictionaries."""
    ticks: list[dict[str, Any]] = []
    try:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="ignore")
        data = json.loads(raw)
        feeds = data.get("feeds", {})
        if not isinstance(feeds, dict):
            return []
        ts = data.get("currentTs", int(time.time() * 1000))
        for instrument_key, feed in feeds.items():
            if not isinstance(feed, dict):
                continue
            ff = feed.get("ff", {}) if isinstance(feed.get("ff", {}), dict) else {}
            mkt = ff.get("marketFF", {}) if isinstance(ff.get("marketFF", {}), dict) else {}
            ltpc = mkt.get("ltpc", {}) if isinstance(mkt.get("ltpc", {}), dict) else {}
            ohlc_obj = mkt.get("marketOHLC", {}) if isinstance(mkt.get("marketOHLC", {}), dict) else {}
            ohlc_list = ohlc_obj.get("ohlc", [{}]) if isinstance(ohlc_obj.get("ohlc", [{}]), list) else [{}]
            ohlc = ohlc_list[0] if ohlc_list else {}
            if not isinstance(ohlc, dict):
                ohlc = {}

            ticks.append(
                {
                    "instrument_key": instrument_key,
                    "ltp": ltpc.get("ltp", 0.0),
                    "close": ltpc.get("cp", 0.0),
                    "open": ohlc.get("open", 0.0),
                    "high": ohlc.get("high", 0.0),
                    "low": ohlc.get("low", 0.0),
                    "volume": ohlc.get("vol", 0),
                    "ts": ts,
                }
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Parse error: %s", exc)
    return ticks


class UpstoxWebSocket:
    """Connects to Upstox feed, normalizes tick frames, and invokes callbacks."""

    def __init__(self, auth_manager: BrokerAuthManager):
        self._auth = auth_manager
        self._callbacks: list[Callable[[list[dict[str, Any]]], Awaitable[None]]] = []
        self._mgr = ReconnectManager(
            ws_url=WS_URL,
            get_headers=self._headers,
            on_message=self._on_raw,
            heartbeat_interval=30,
        )
        self._connect_task: asyncio.Task | None = None

    async def connect(self) -> None:
        """Start the reconnect loop in the background."""
        try:
            if self._connect_task and not self._connect_task.done():
                return
            self._connect_task = asyncio.create_task(self._mgr.connect())
        except Exception as exc:  # noqa: BLE001
            logger.error("WebSocket connect failed: %s", exc)

    async def subscribe(self, symbols: list[str], mode: str = "full") -> None:
        """Subscribe to one or more symbols."""
        try:
            if not symbols:
                return
            keys = [self._to_key(symbol) for symbol in symbols]
            await self._mgr.send(
                {
                    "guid": f"sub-{int(time.time())}",
                    "method": "sub",
                    "data": {"mode": mode, "instrumentKeys": keys},
                }
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Subscribe failed: %s", exc)

    def on_tick(self, callback: Callable[[list[dict[str, Any]]], Awaitable[None]]) -> None:
        """Register an async callback for parsed tick batches."""
        self._callbacks.append(callback)

    async def close(self) -> None:
        """Stop the reconnect loop and close the socket."""
        try:
            await self._mgr.close()
            if self._connect_task and not self._connect_task.done():
                self._connect_task.cancel()
        except Exception as exc:  # noqa: BLE001
            logger.error("WebSocket close failed: %s", exc)

    async def _headers(self) -> dict[str, str]:
        try:
            token = await self._auth.get_access_token()
            return {"Authorization": f"Bearer {token}", "Api-Version": "2.0"}
        except Exception as exc:  # noqa: BLE001
            logger.error("Header generation failed: %s", exc)
            raise

    async def _on_raw(self, raw: Any) -> None:
        try:
            ticks = _parse(raw)
            if not ticks:
                return
            for callback in self._callbacks:
                try:
                    result = callback(ticks)
                    if asyncio.iscoroutine(result):
                        await result
                except Exception as exc:  # noqa: BLE001
                    logger.error("Tick callback error: %s", exc)
        except Exception as exc:  # noqa: BLE001
            logger.error("Raw tick handling failed: %s", exc)

    @staticmethod
    def _to_key(symbol: str) -> str:
        s = (symbol or "").upper().replace(".NS", "").replace(".BO", "")
        return f"NSE_EQ|{s}"


"""Central market-data hub that caches prices and republishes ticks to the event bus."""
from __future__ import annotations

import logging
import time
from typing import Optional

try:
    from backend.execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from backend.market_data.upstox_websocket import UpstoxWebSocket  # type: ignore
except ModuleNotFoundError:  # noqa: BLE001
    from execution.auth.broker_auth_manager import BrokerAuthManager  # type: ignore
    from market_data.upstox_websocket import UpstoxWebSocket  # type: ignore

logger = logging.getLogger(__name__)


class MarketDataEngine:
    """Keeps an in-memory quote cache and emits market.tick events."""

    def __init__(self, event_bus, auth_manager: Optional[BrokerAuthManager] = None):
        self._bus = event_bus
        self._auth = auth_manager or BrokerAuthManager("upstox")
        self._ws = UpstoxWebSocket(self._auth)
        self._cache: dict[str, dict] = {}
        self._cache_updated_at: dict[str, float] = {}
        self._stale_threshold: float = 120.0  # seconds
        self._ws.on_tick(self._on_ticks)

    async def start(self) -> None:
        """Start the WebSocket connection."""
        try:
            logger.info("MarketDataEngine starting")
            await self._ws.connect()
        except Exception as exc:  # noqa: BLE001
            logger.error("MarketDataEngine start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the WebSocket connection."""
        try:
            await self._ws.close()
        except Exception as exc:  # noqa: BLE001
            logger.error("MarketDataEngine stop failed: %s", exc)

    async def subscribe(self, symbols: list[str], mode: str = "full") -> bool:
        """Subscribe to a list of symbols. Returns True on success."""
        try:
            await self._ws.subscribe(symbols, mode)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("MarketDataEngine subscribe failed: %s", exc)
            return False

    def get_ltp(self, symbol: str) -> float:
        """Return the latest cached last-traded price. Returns 0.0 if stale."""
        sym = (symbol or "").upper()
        updated_at = self._cache_updated_at.get(sym, 0.0)
        if updated_at > 0 and (time.time() - updated_at) > self._stale_threshold:
            logger.warning("Stale price for %s (%.0fs old)", sym, time.time() - updated_at)
            return 0.0
        return float(self._cache.get(sym, {}).get("ltp", 0.0) or 0.0)

    def get_snapshot(self, symbol: str) -> dict:
        """Return the full cached tick snapshot. Returns empty dict if stale."""
        sym = (symbol or "").upper()
        updated_at = self._cache_updated_at.get(sym, 0.0)
        if updated_at > 0 and (time.time() - updated_at) > self._stale_threshold:
            return {}
        return dict(self._cache.get(sym, {}))

    async def _on_ticks(self, ticks: list[dict]) -> None:
        try:
            for tick in ticks:
                ikey = str(tick.get("instrument_key", ""))
                symbol = (ikey.split("|")[-1] if "|" in ikey else ikey).upper()
                if not symbol:
                    continue
                self._cache[symbol] = tick
                self._cache_updated_at[symbol] = time.time()
                await self._bus.publish(
                    "market.tick",
                    {
                        "symbol": symbol,
                        "ltp": tick.get("ltp", 0.0),
                        "open": tick.get("open", 0.0),
                        "high": tick.get("high", 0.0),
                        "low": tick.get("low", 0.0),
                        "close": tick.get("close", 0.0),
                        "volume": tick.get("volume", 0),
                        "timestamp": tick.get("ts"),
                    },
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("Tick fan-out failed: %s", exc)


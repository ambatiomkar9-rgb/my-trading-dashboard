"""Central market-data hub that caches prices and republishes ticks to the event bus."""
from __future__ import annotations

import logging
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

    async def subscribe(self, symbols: list[str], mode: str = "full") -> None:
        """Subscribe to a list of symbols."""
        try:
            await self._ws.subscribe(symbols, mode)
        except Exception as exc:  # noqa: BLE001
            logger.error("MarketDataEngine subscribe failed: %s", exc)

    def get_ltp(self, symbol: str) -> float:
        """Return the latest cached last-traded price."""
        return float(self._cache.get((symbol or "").upper(), {}).get("ltp", 0.0) or 0.0)

    def get_snapshot(self, symbol: str) -> dict:
        """Return the full cached tick snapshot."""
        return dict(self._cache.get((symbol or "").upper(), {}))

    async def _on_ticks(self, ticks: list[dict]) -> None:
        try:
            for tick in ticks:
                ikey = str(tick.get("instrument_key", ""))
                symbol = (ikey.split("|")[-1] if "|" in ikey else ikey).upper()
                if not symbol:
                    continue
                self._cache[symbol] = tick
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


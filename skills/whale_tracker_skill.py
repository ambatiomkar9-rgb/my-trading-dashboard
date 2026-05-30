"""Hyperliquid whale tracking and smart-money analytics."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WhaleAlert:
    """Large transaction or flow regime alert."""

    coin: str
    side: str
    notional_usd: float
    reason: str
    tx_hash: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class WhaleTrackerSkill:
    """
    Whale tracking with Hyperliquid market data.

    Features:
    - Whale accumulation detection
    - Smart money sentiment
    - Direction change tracking
    - Large transaction alerts
    """

    def __init__(
        self,
        info_url: str = "https://api.hyperliquid.xyz/info",
        large_tx_threshold_usd: float = 250_000.0,
        accumulation_threshold_usd: float = 1_000_000.0,
        timeout_sec: int = 20,
    ) -> None:
        self.info_url = info_url
        self.large_tx_threshold_usd = large_tx_threshold_usd
        self.accumulation_threshold_usd = accumulation_threshold_usd
        self.timeout_sec = timeout_sec
        self._last_direction: Dict[str, str] = {}

    async def fetch_recent_trades(self, coin: str) -> List[Dict[str, Any]]:
        """Fetch recent trades from Hyperliquid."""
        payload = {"type": "recentTrades", "coin": coin.upper()}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_sec)) as session:
            async with session.post(self.info_url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if not isinstance(data, list):
                    raise ValueError("Unexpected Hyperliquid recentTrades response")
                return data

    async def fetch_context(self, coin: str) -> Dict[str, Any]:
        """Fetch market context for normalization."""
        payload = {"type": "metaAndAssetCtxs"}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout_sec)) as session:
            async with session.post(self.info_url, json=payload) as response:
                response.raise_for_status()
                data = await response.json()
                if not isinstance(data, list) or len(data) < 2:
                    return {"coin": coin.upper(), "context_available": False}
                return {"coin": coin.upper(), "context_available": True, "raw": data}

    async def analyze_whale_activity(self, coin: str = "BTC") -> Dict[str, Any]:
        """Compute whale flow analytics and alerts."""
        try:
            trades = await self.fetch_recent_trades(coin)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Whale tracker fetch failed coin=%s", coin)
            return {"coin": coin.upper(), "error": str(exc), "alerts": [], "sentiment": "unknown"}

        alerts = self._detect_large_transactions(coin.upper(), trades)
        accumulation = self._detect_accumulation(coin.upper(), trades)
        sentiment = self._smart_money_sentiment(trades)
        direction_change = self._track_direction_change(coin.upper(), sentiment["direction"])

        if accumulation["detected"]:
            alerts.append(
                WhaleAlert(
                    coin=coin.upper(),
                    side=accumulation["side"],
                    notional_usd=accumulation["net_notional_usd"],
                    reason="whale_accumulation_detected",
                )
            )
        if direction_change["changed"]:
            alerts.append(
                WhaleAlert(
                    coin=coin.upper(),
                    side=direction_change["to"],
                    notional_usd=abs(accumulation["net_notional_usd"]),
                    reason=f"direction_change_{direction_change['from']}_to_{direction_change['to']}",
                )
            )

        return {
            "coin": coin.upper(),
            "trade_count": len(trades),
            "sentiment": sentiment["label"],
            "direction": sentiment["direction"],
            "net_notional_usd": accumulation["net_notional_usd"],
            "accumulation": accumulation,
            "direction_change": direction_change,
            "alerts": [asdict(a) for a in alerts],
        }

    def _detect_large_transactions(self, coin: str, trades: List[Dict[str, Any]]) -> List[WhaleAlert]:
        """Flag large notional transactions."""
        alerts: List[WhaleAlert] = []
        for trade in trades:
            try:
                px = float(trade.get("px") or trade.get("price") or 0)
                sz = float(trade.get("sz") or trade.get("size") or 0)
                side = "buy" if bool(trade.get("side", "B").lower().startswith("b")) else "sell"
                notional = px * sz
            except Exception:
                continue
            if notional >= self.large_tx_threshold_usd:
                alerts.append(
                    WhaleAlert(
                        coin=coin,
                        side=side,
                        notional_usd=notional,
                        reason="large_transaction",
                        tx_hash=trade.get("hash") or trade.get("txHash"),
                    )
                )
        return alerts

    def _detect_accumulation(self, coin: str, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect buy/sell imbalance as accumulation or distribution."""
        buy_notional = 0.0
        sell_notional = 0.0
        for trade in trades:
            try:
                px = float(trade.get("px") or trade.get("price") or 0)
                sz = float(trade.get("sz") or trade.get("size") or 0)
                side = "buy" if bool(trade.get("side", "B").lower().startswith("b")) else "sell"
                n = px * sz
            except Exception:
                continue
            if side == "buy":
                buy_notional += n
            else:
                sell_notional += n
        net = buy_notional - sell_notional
        detected = abs(net) >= self.accumulation_threshold_usd
        side = "buy" if net > 0 else "sell"
        return {
            "coin": coin,
            "buy_notional_usd": buy_notional,
            "sell_notional_usd": sell_notional,
            "net_notional_usd": net,
            "detected": detected,
            "side": side,
        }

    def _smart_money_sentiment(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate sentiment from flow imbalance."""
        buy_notional = 0.0
        sell_notional = 0.0
        for trade in trades:
            try:
                px = float(trade.get("px") or trade.get("price") or 0)
                sz = float(trade.get("sz") or trade.get("size") or 0)
                side = "buy" if bool(trade.get("side", "B").lower().startswith("b")) else "sell"
                notional = px * sz
            except Exception:
                continue
            if side == "buy":
                buy_notional += notional
            else:
                sell_notional += notional
        total = buy_notional + sell_notional
        if total <= 0:
            return {"label": "neutral", "direction": "neutral", "score": 0.0}
        ratio = (buy_notional - sell_notional) / total
        if ratio > 0.2:
            label = "bullish_whales"
            direction = "up"
        elif ratio < -0.2:
            label = "bearish_whales"
            direction = "down"
        else:
            label = "neutral_whales"
            direction = "neutral"
        return {"label": label, "direction": direction, "score": ratio}

    def _track_direction_change(self, coin: str, direction: str) -> Dict[str, Any]:
        """Track directional regime transitions."""
        previous = self._last_direction.get(coin, "unknown")
        changed = previous != "unknown" and previous != direction
        self._last_direction[coin] = direction
        return {"coin": coin, "from": previous, "to": direction, "changed": changed}

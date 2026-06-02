"""Whale Intelligence Agent — tracks large institutional trades and smart money flows."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

CACHE_TTL = 1800  # 30 minutes


def _detect_whale_activity(trades: list[dict], volume_threshold: float = 100000) -> dict[str, Any]:
    """Analyze block deals and large trades for whale activity signals."""
    signals = []
    bullish_volume = 0.0
    bearish_volume = 0.0

    for trade in trades:
        qty = int(trade.get("quantity", 0) or 0)
        price = float(trade.get("price", 0) or 0)
        value = qty * price

        if value < volume_threshold * 100:
            continue

        side = str(trade.get("side", "")).lower()
        symbol = str(trade.get("symbol", "")).upper()

        if side == "buy":
            bullish_volume += value
            signals.append({
                "type": "whale_buy",
                "symbol": symbol,
                "quantity": qty,
                "value": round(value, 2),
                "impact": "bullish",
            })
        elif side == "sell":
            bearish_volume += value
            signals.append({
                "type": "whale_sell",
                "symbol": symbol,
                "quantity": qty,
                "value": round(value, 2),
                "impact": "bearish",
            })

    total_volume = bullish_volume + bearish_volume
    if total_volume == 0:
        return {"label": "no_activity", "signals": [], "bullish_volume": 0, "bearish_volume": 0}

    net_flow = bullish_volume - bearish_volume
    net_pct = (net_flow / total_volume * 100) if total_volume else 0

    if net_pct > 20:
        label = "bullish_accumulation"
    elif net_pct < -20:
        label = "bearish_distribution"
    else:
        label = "neutral"

    return {
        "label": label,
        "net_flow": round(net_flow, 2),
        "net_pct": round(net_pct, 1),
        "bullish_volume": round(bullish_volume, 2),
        "bearish_volume": round(bearish_volume, 2),
        "signals": signals,
        "trade_count": len(signals),
    }


class WhaleIntelligenceAgent:
    """
    Monitors NSE block deals and large trades to detect institutional activity.

    Data sources:
    - NSE Bhavcopy (daily)
    - NSE Block Deals API
    - Upstox bulk deals endpoint
    """

    def __init__(self, event_bus: Any) -> None:
        self._bus = event_bus
        self._cache: dict[str, Any] = {}
        self._running = False

    async def start(self) -> None:
        """Run periodic whale analysis loop."""
        try:
            self._running = True
            logger.info("WhaleIntelligenceAgent started")
            while self._running:
                await self._analyze()
                await asyncio.sleep(1800)  # 30 minutes
        except Exception as exc:  # noqa: BLE001
            logger.error("WhaleIntelligenceAgent start failed: %s", exc)

    async def stop(self) -> None:
        self._running = False

    async def get_whale_snapshot(self) -> Optional[dict]:
        """Return the latest cached whale analysis."""
        cached = self._cache.get("whale")
        if cached and (time.time() - cached.get("fetched_at", 0)) < CACHE_TTL:
            return cached
        return None

    async def _analyze(self) -> None:
        """Fetch block deal data and detect whale activity."""
        try:
            cached = self._cache.get("whale")
            if cached and (time.time() - cached.get("fetched_at", 0)) < CACHE_TTL:
                return

            # Fetch NSE block deals
            block_deals = await self._fetch_nse_block_deals()
            if not block_deals:
                block_deals = await self._fetch_upstox_bulk_deals()

            if not block_deals:
                return

            analysis = _detect_whale_activity(block_deals)
            analysis["fetched_at"] = time.time()
            self._cache["whale"] = analysis

            await self._bus.publish("whale.activity", analysis)
            if analysis["signals"]:
                logger.info(
                    "Whale activity: %s (net_flow=%.0f, trades=%d)",
                    analysis["label"], analysis["net_flow"], analysis["trade_count"],
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("Whale analysis failed: %s", exc)

    async def _fetch_nse_block_deals(self) -> list[dict]:
        """Fetch today's block deals from NSE."""
        try:
            import datetime
            today = datetime.date.today().strftime("%d-%b-%Y").upper()
            url = f"https://archives.nseindia.com/content/block_deal/block_deal_{today}.csv"
            async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return []
                lines = resp.text.strip().split('\n')
                if len(lines) < 2:
                    return []

                trades = []
                for line in lines[1:]:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 5:
                        trades.append({
                            "symbol": parts[0],
                            "side": "buy" if "B" in parts[1].upper() else "sell",
                            "quantity": int(parts[2]) if parts[2].isdigit() else 0,
                            "price": float(parts[3]) if parts[3].replace('.', '').isdigit() else 0,
                            "client": parts[4] if len(parts) > 4 else "",
                        })
                return trades
        except Exception as exc:  # noqa: BLE001
            logger.debug("NSE block deals fetch failed: %s", exc)
            return []

    async def _fetch_upstox_bulk_deals(self) -> list[dict]:
        """Fetch bulk deals from Upstox API."""
        try:
            import datetime
            today = datetime.date.today().strftime("%Y-%m-%d")
            url = f"https://api.upstox.com/v2/market-quote/bulk-deals"
            async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
                resp = await client.get(url, params={"date": today})
                if resp.status_code != 200:
                    return []
                data = resp.json()
                deals = data.get("data", []) if isinstance(data, dict) else []
                trades = []
                for deal in deals:
                    trades.append({
                        "symbol": str(deal.get("symbol", "")),
                        "side": "buy" if str(deal.get("deal_type", "")).lower() == "buy" else "sell",
                        "quantity": int(deal.get("quantity", 0)),
                        "price": float(deal.get("price", 0)),
                        "client": str(deal.get("client_name", "")),
                    })
                return trades
        except Exception as exc:  # noqa: BLE001
            logger.debug("Upstox bulk deals fetch failed: %s", exc)
            return []

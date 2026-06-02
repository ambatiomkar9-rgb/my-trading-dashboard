"""Macro Intelligence Agent — analyzes macro-economic indicators and their market impact."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

CACHE_TTL = 3600  # 1 hour


# ── Macro Data Sources ───────────────────────────────────────────────────────

# Free macro data via yfinance proxy tickers
MACRO_TICKERS = {
    "usd_inr": "USDINR=X",
    "nifty_50": "^NSEI",
    "sensex": "^BSESN",
    "india_vix": "^INDIAVIX",
    "us_10y": "^TNX",
    "gold": "GC=F",
    "crude_oil": "CL=F",
    "dxy": "DX-Y.NYB",
    "s_p_500": "^GSPC",
    "nasdaq": "^IXIC",
}


def _score_macro_impact(data: dict[str, Any]) -> dict[str, Any]:
    """Score macro conditions and their impact on Indian equities."""
    signals = []
    overall_bias = 0.0

    # USD/INR impact (weaker INR = negative for imports, positive for IT exports)
    usd_inr = data.get("usd_inr", {})
    if usd_inr.get("change_pct", 0) > 0.5:
        signals.append({"factor": "USD/INR rising", "impact": "negative", "weight": -0.3})
        overall_bias -= 0.3
    elif usd_inr.get("change_pct", 0) < -0.5:
        signals.append({"factor": "USD/INR falling", "impact": "positive", "weight": 0.2})
        overall_bias += 0.2

    # crude oil impact (higher oil = negative for India)
    crude = data.get("crude_oil", {})
    if crude.get("change_pct", 0) > 2.0:
        signals.append({"factor": "Crude oil surging", "impact": "negative", "weight": -0.4})
        overall_bias -= 0.4
    elif crude.get("change_pct", 0) < -2.0:
        signals.append({"factor": "Crude oil falling", "impact": "positive", "weight": 0.3})
        overall_bias += 0.3

    # US 10Y yield (higher yields = capital outflow risk)
    us_10y = data.get("us_10y", {})
    if us_10y.get("change_pct", 0) > 3.0:
        signals.append({"factor": "US yields rising", "impact": "negative", "weight": -0.3})
        overall_bias -= 0.3
    elif us_10y.get("change_pct", 0) < -3.0:
        signals.append({"factor": "US yields falling", "impact": "positive", "weight": 0.2})
        overall_bias += 0.2

    # India VIX (high VIX = fear = risk-off)
    vix = data.get("india_vix", {})
    vix_val = float(vix.get("last", 0) or 0)
    if vix_val > 25:
        signals.append({"factor": f"India VIX elevated ({vix_val:.1f})", "impact": "negative", "weight": -0.4})
        overall_bias -= 0.4
    elif vix_val < 12:
        signals.append({"factor": f"India VIX low ({vix_val:.1f})", "impact": "positive", "weight": 0.2})
        overall_bias += 0.2

    # DXY strength (strong USD = negative for EM)
    dxy = data.get("dxy", {})
    if dxy.get("change_pct", 0) > 0.5:
        signals.append({"factor": "Dollar strengthening", "impact": "negative", "weight": -0.2})
        overall_bias -= 0.2
    elif dxy.get("change_pct", 0) < -0.5:
        signals.append({"factor": "Dollar weakening", "impact": "positive", "weight": 0.2})
        overall_bias += 0.2

    # Gold (safe haven demand = risk-off)
    gold = data.get("gold", {})
    if gold.get("change_pct", 0) > 1.5:
        signals.append({"factor": "Gold rallying (risk-off)", "impact": "negative", "weight": -0.2})
        overall_bias -= 0.2

    # Nifty/Sensex momentum
    nifty = data.get("nifty_50", {})
    if nifty.get("change_pct", 0) > 1.0:
        signals.append({"factor": "Nifty strong momentum", "impact": "positive", "weight": 0.3})
        overall_bias += 0.3
    elif nifty.get("change_pct", 0) < -1.0:
        signals.append({"factor": "Nifty weak momentum", "impact": "negative", "weight": -0.3})
        overall_bias -= 0.3

    # Determine label
    if overall_bias > 0.3:
        label = "bullish"
    elif overall_bias < -0.3:
        label = "bearish"
    else:
        label = "neutral"

    return {
        "overall_bias": round(overall_bias, 2),
        "label": label,
        "signals": signals,
        "data": data,
    }


class MacroIntelligenceAgent:
    """Fetches macro-economic data and publishes market-wide impact signals."""

    def __init__(self, event_bus: Any) -> None:
        self._bus = event_bus
        self._cache: dict[str, Any] = {}
        self._running = False

    async def start(self) -> None:
        """Run periodic macro analysis loop."""
        try:
            self._running = True
            logger.info("MacroIntelligenceAgent started")
            while self._running:
                await self._analyze()
                await asyncio.sleep(1800)  # 30 minutes
        except Exception as exc:  # noqa: BLE001
            logger.error("MacroIntelligenceAgent start failed: %s", exc)

    async def stop(self) -> None:
        self._running = False

    async def get_macro_snapshot(self) -> Optional[dict]:
        """Return the latest cached macro analysis."""
        cached = self._cache.get("macro")
        if cached and (time.time() - cached.get("fetched_at", 0)) < CACHE_TTL:
            return cached
        return None

    async def _analyze(self) -> None:
        """Fetch macro data and compute market impact."""
        try:
            cached = self._cache.get("macro")
            if cached and (time.time() - cached.get("fetched_at", 0)) < CACHE_TTL:
                return

            import yfinance as yf

            data = {}
            for key, ticker in MACRO_TICKERS.items():
                try:
                    t = yf.Ticker(ticker)
                    hist = t.history(period="5d")
                    if hist is not None and not hist.empty and len(hist) >= 2:
                        last = float(hist["Close"].iloc[-1])
                        prev = float(hist["Close"].iloc[-2])
                        change_pct = ((last - prev) / prev * 100) if prev else 0
                        data[key] = {
                            "last": last,
                            "prev": prev,
                            "change_pct": round(change_pct, 2),
                        }
                except Exception:
                    continue

            if not data:
                return

            analysis = _score_macro_impact(data)
            analysis["fetched_at"] = time.time()
            self._cache["macro"] = analysis

            await self._bus.publish("macro.update", analysis)
            logger.info("Macro analysis: %s (bias=%.2f)", analysis["label"], analysis["overall_bias"])
        except Exception as exc:  # noqa: BLE001
            logger.error("Macro analysis failed: %s", exc)

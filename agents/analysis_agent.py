"""Analysis agent: turns real market data + other agent outputs into an explanation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from trading_system.integrations.hermes_client import HermesClient

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AnalysisBundle:
    symbol: str
    timeframe: str
    market_data: Dict[str, Any]
    technical: Dict[str, Any]
    news: Dict[str, Any]
    macro: Optional[Dict[str, Any]] = None


class AnalysisAgent:
    """Compose an analysis narrative with Hermes support."""

    def __init__(self, hermes: Optional[HermesClient] = None) -> None:
        self.hermes = hermes or HermesClient()

    async def analyze(self, bundle: AnalysisBundle) -> Dict[str, Any]:
        # Minimal structured output; boss agent formats for user.
        sentiment = (bundle.news.get("sentiment") or {}).get("label", "unknown")
        tech_signal = bundle.technical.get("signal", "hold")
        trend = bundle.technical.get("trend", "unknown")
        price = float(bundle.market_data.get("price") or 0.0)

        prompt = (
            "You are a trading analyst. Given the data, write a concise report with:\n"
            "1) Trend + technical signal\n"
            "2) News sentiment\n"
            "3) Key levels / risks\n"
            "4) A one-line plan (entry/stop/targets) for paper trading only\n\n"
            f"Symbol: {bundle.symbol}\n"
            f"Timeframe: {bundle.timeframe}\n"
            f"Price: {price}\n"
            f"Technical: {bundle.technical}\n"
            f"News: {bundle.news}\n"
            f"Macro: {bundle.macro or {}}\n"
        )
        # Hermes is a helper; if unavailable, fall back to a deterministic summary.
        text = await _maybe_to_thread(self.hermes.query, prompt)
        if not text or text.startswith("HERMES_"):
            text = (
                f"{bundle.symbol} ({bundle.timeframe}) price={price:.2f}\n"
                f"trend={trend} signal={tech_signal}\n"
                f"news_sentiment={sentiment}\n"
                "Note: Hermes unavailable; this is a minimal summary."
            )

        return {
            "symbol": bundle.symbol,
            "timeframe": bundle.timeframe,
            "price": price,
            "trend": trend,
            "signal": tech_signal,
            "news_sentiment": sentiment,
            "report": text,
        }


async def _maybe_to_thread(fn, *args):
    import asyncio

    return await asyncio.to_thread(fn, *args)


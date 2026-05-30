"""News and sentiment intelligence skill."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List

import yfinance as yf

logger = logging.getLogger(__name__)


class NewsIntelligenceSkill:
    """Fetch ticker news and compute lightweight sentiment."""

    POSITIVE_WORDS = {"beat", "growth", "upgrade", "surge", "profit", "record", "bullish", "strong"}
    NEGATIVE_WORDS = {"miss", "downgrade", "decline", "loss", "lawsuit", "bearish", "weak", "drop"}

    async def fetch_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch news via NewsAPI (if configured) or yfinance fallback."""
        key = os.getenv("NEWSAPI_KEY", "").strip()
        if key:
            try:
                return await asyncio.to_thread(
                    lambda: self._fetch_newsapi(symbol=symbol, limit=limit, api_key=key)
                )
            except Exception as exc:  # noqa: BLE001
                # Never block the agents on NewsAPI flakiness; fall back to yfinance.
                logger.warning("NewsAPI fetch failed; falling back to yfinance symbol=%s error=%s", symbol, exc)
        ticker = yf.Ticker(symbol)
        news = await asyncio.to_thread(lambda: ticker.news)
        if not news:
            return []
        return news[:limit]

    def _fetch_newsapi(self, symbol: str, limit: int, api_key: str) -> List[Dict[str, Any]]:
        # NewsAPI does not like exchange suffixes; keep a readable query.
        query = symbol.replace(".NS", "").replace("-USD", "").replace("/", " ")
        params = {
            "q": query,
            "pageSize": str(max(1, min(50, int(limit)))),
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": api_key,
        }
        url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, method="GET")
        # Keep this very short so agents stay responsive.
        timeout_sec = float(os.getenv("NEWSAPI_TIMEOUT_SEC", "4.5"))
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            body = resp.read().decode("utf-8")
        data = json.loads(body) if body else {}
        articles = data.get("articles") or []
        out: List[Dict[str, Any]] = []
        for a in articles[:limit]:
            out.append(
                {
                    "title": a.get("title") or "",
                    "link": a.get("url") or "",
                    "source": (a.get("source") or {}).get("name"),
                    "publishedAt": a.get("publishedAt"),
                }
            )
        return out

    def score_sentiment(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Lexicon sentiment score for headlines."""
        score = 0
        analyzed: List[Dict[str, Any]] = []
        for item in items:
            title = (item.get("title") or "").lower()
            words = set(title.split())
            pos_hits = len(words & self.POSITIVE_WORDS)
            neg_hits = len(words & self.NEGATIVE_WORDS)
            item_score = pos_hits - neg_hits
            score += item_score
            analyzed.append({"title": item.get("title", ""), "score": item_score, "link": item.get("link")})
        label = "neutral"
        if score > 2:
            label = "positive"
        elif score < -2:
            label = "negative"
        return {"label": label, "aggregate_score": score, "items": analyzed}

    async def analyze(self, symbol: str) -> Dict[str, Any]:
        """Fetch and score sentiment for a symbol."""
        try:
            items = await self.fetch_news(symbol)
            sentiment = self.score_sentiment(items)
            return {"symbol": symbol, "count": len(items), "sentiment": sentiment}
        except Exception as exc:  # noqa: BLE001
            logger.exception("News analysis failed symbol=%s", symbol)
            return {"symbol": symbol, "error": str(exc), "count": 0, "sentiment": {"label": "unknown"}}

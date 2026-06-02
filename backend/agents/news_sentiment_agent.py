"""NewsAPI-backed sentiment agent that publishes symbol scores to the event bus."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
NEWSAPI_URL = "https://newsapi.org/v2/everything"
CACHE_TTL = 3600


def _score_text(text: str) -> float:
    """Return a sentiment polarity score in the range -1.0..+1.0."""
    if not text:
        return 0.0
    try:
        from textblob import TextBlob

        return float(TextBlob(text).sentiment.polarity)
    except ImportError:
        positive = ["growth", "profit", "record", "beat", "strong", "surge", "gain", "up", "bullish", "buy"]
        negative = ["loss", "decline", "miss", "fall", "weak", "cut", "down", "bearish", "sell", "risk"]
        text_l = text.lower()
        score = sum(1 for word in positive if word in text_l)
        score -= sum(1 for word in negative if word in text_l)
        return max(-1.0, min(1.0, score / 5.0))
    except Exception as exc:  # noqa: BLE001
        logger.debug("Sentiment scoring fallback failed: %s", exc)
        return 0.0


class NewsSentimentAgent:
    """Fetches and caches recent symbol news, then emits sentiment events."""

    def __init__(self, event_bus: Any, watchlist: list[str]):
        self._bus = event_bus
        self._watchlist = [str(symbol).replace(".NS", "").replace(".BO", "").upper() for symbol in watchlist]
        self._cache: dict[str, dict] = {}
        self._running = False

    def set_watchlist(self, watchlist: list[str]) -> None:
        """Replace the active watchlist in memory."""
        self._watchlist = [str(symbol).replace(".NS", "").replace(".BO", "").upper() for symbol in watchlist]

    def add_symbol(self, symbol: str) -> None:
        """Add one symbol to the active watchlist."""
        sym = str(symbol).replace(".NS", "").replace(".BO", "").upper().strip()
        if sym and sym not in self._watchlist:
            self._watchlist.append(sym)

    def remove_symbol(self, symbol: str) -> None:
        """Remove one symbol from the active watchlist."""
        sym = str(symbol).replace(".NS", "").replace(".BO", "").upper().strip()
        self._watchlist = [item for item in self._watchlist if item != sym]

    async def start(self) -> None:
        """Run the periodic sentiment loop."""
        try:
            self._running = True
            while self._running:
                for symbol in self._watchlist:
                    try:
                        await self._analyze(symbol)
                    except Exception as exc:  # noqa: BLE001
                        logger.error("News error for %s: %s", symbol, exc)
                    await asyncio.sleep(2)
                await asyncio.sleep(1800)
        except Exception as exc:  # noqa: BLE001
            logger.error("NewsSentimentAgent start failed: %s", exc)

    async def stop(self) -> None:
        """Stop the periodic loop."""
        try:
            self._running = False
        except Exception as exc:  # noqa: BLE001
            logger.error("NewsSentimentAgent stop failed: %s", exc)

    async def get_sentiment(self, symbol: str) -> Optional[dict]:
        """Return the cached sentiment snapshot, if any."""
        try:
            return self._cache.get(str(symbol).upper())
        except Exception as exc:  # noqa: BLE001
            logger.error("get_sentiment failed: %s", exc)
            return None

    async def _analyze(self, symbol: str) -> None:
        """Fetch headlines, score them, and publish a symbol-level sentiment payload."""
        try:
            sym = str(symbol).upper()
            cached = self._cache.get(sym)
            if cached and (time.time() - float(cached.get("fetched_at", 0))) < CACHE_TTL:
                return

            newsapi_key = os.getenv("NEWSAPI_KEY", "").strip() or NEWSAPI_KEY
            if not newsapi_key:
                logger.warning("NEWSAPI_KEY not set - news agent disabled")
                return

            articles = await self._fetch(sym, newsapi_key=newsapi_key)
            if not articles:
                return

            scores: list[float] = []
            headlines: list[str] = []
            for article in articles[:10]:
                title = str(article.get("title") or "")
                description = str(article.get("description") or "")
                if title:
                    headlines.append(title)
                scores.append(_score_text(f"{title} {description}"))

            if not scores:
                return

            avg_raw = sum(scores) / len(scores)
            sentiment_100 = round((avg_raw + 1.0) / 2.0 * 100.0, 1)
            result = {
                "symbol": sym,
                "score": sentiment_100,
                "label": "bullish" if sentiment_100 > 60 else "bearish" if sentiment_100 < 40 else "neutral",
                "article_count": len(scores),
                "top_headlines": headlines[:3],
                "fetched_at": time.time(),
            }
            self._cache[sym] = result
            await self._bus.publish("news.sentiment", result)
            logger.info("News sentiment %s: %.1f (%s)", sym, sentiment_100, result["label"])
        except Exception as exc:  # noqa: BLE001
            logger.error("_analyze failed for %s: %s", symbol, exc)

    async def _fetch(self, symbol: str, newsapi_key: str | None = None) -> list[dict]:
        """Fetch recent articles for a symbol from NewsAPI."""
        from backend.infra.circuit_breaker import get_breaker

        breaker = get_breaker("newsapi", failure_threshold=5, recovery_timeout=300)
        if not breaker.allow_request():
            logger.warning("NewsAPI circuit breaker OPEN — skipping %s", symbol)
            return []

        try:
            key = (newsapi_key or os.getenv("NEWSAPI_KEY", "").strip() or NEWSAPI_KEY).strip()
            params = {
                "q": symbol,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10,
                "apiKey": key,
            }
            exclude = os.getenv("NEWSAPI_EXCLUDE_DOMAINS", "").strip()
            if exclude:
                params["excludeDomains"] = exclude

            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(NEWSAPI_URL, params=params)
                resp.raise_for_status()
                payload = resp.json()
                breaker.record_success()
                return payload.get("articles", []) if isinstance(payload, dict) else []
        except httpx.HTTPStatusError as exc:
            breaker.record_failure()
            if exc.response.status_code == 429:
                logger.warning("NewsAPI rate limit hit. Sleeping 1h.")
                await asyncio.sleep(3600)
            elif exc.response.status_code == 401:
                logger.error("NewsAPI key invalid. Check NEWSAPI_KEY env var.")
            return []
        except Exception as exc:  # noqa: BLE001
            breaker.record_failure()
            logger.error("NewsAPI fetch error: %s", exc)
            return []

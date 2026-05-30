"""Watchlist executor: polls the cloud dashboard watchlist and emits signals.

Design notes:
- Runs locally on the laptop (next to Ollama and agents).
- Stores watchlist + pending approvals in the cloud dashboard (Render).
- Uses existing local skills (technical/news) and posts a BUY signal when conditions match.
- Cooldown is enforced server-side via /alerts/buy-signal (default 60s).
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

# Ensure `import trading_system.*` works no matter where we launch from.
_PKG_DIR = Path(__file__).resolve().parents[1]  # .../trading_system
_REPO_ROOT = _PKG_DIR.parent
sys.path.insert(0, str(_REPO_ROOT))
load_dotenv(_PKG_DIR / ".env")

_LOGS_DIR = _PKG_DIR / "logs"
_LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(_LOGS_DIR / f"watchlist_executor_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

from trading_system.skills.news_intelligence_skill import NewsIntelligenceSkill
from trading_system.skills.technical_analysis_skill import TechnicalAnalysisSkill

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://my-trading-dashboard-8.onrender.com").rstrip("/")
CHECK_INTERVAL_SECONDS = int(os.getenv("WATCHLIST_CHECK_INTERVAL_SEC", "300"))  # 5 minutes default


def _safe_json(res: urllib.response.addinfourl) -> Any:
    body = res.read().decode("utf-8")
    return json.loads(body) if body else {}


def _get_json(url: str, timeout: int = 15) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return _safe_json(resp)


def _post_json(url: str, payload: dict, timeout: int = 15) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return _safe_json(resp)


def post_status(status: str, task: str = "", progress: int = 0) -> None:
    payload = {
        "agent_id": "watchlist_executor",
        "status": status,
        "task": task,
        "progress": progress,
        "timestamp": datetime.now().isoformat(),
    }
    try:
        _post_json(f"{DASHBOARD_URL}/agent-status", payload, timeout=10)
    except Exception:
        pass


def _score_technical(snapshot: Any) -> float:
    # Very lightweight: treat buy_bias as stronger, else neutral.
    sig = str(getattr(snapshot, "signal", "")).lower()
    if sig == "buy_bias":
        return 80.0
    if sig == "sell_bias":
        return 20.0
    return 50.0


def _score_news(sentiment: Dict[str, Any]) -> float:
    label = str(sentiment.get("label") or "neutral").lower()
    agg = float(sentiment.get("aggregate_score") or 0.0)
    if label == "positive":
        return min(90.0, 60.0 + agg * 5.0)
    if label == "negative":
        return max(10.0, 40.0 + agg * 5.0)
    return 50.0


def _overall(tech: float, news: float, fund: float, risk: float) -> float:
    return (tech + news + fund + risk) / 4.0


async def _analyze_symbol(symbol: str, timeframe: str) -> Tuple[Optional[float], Dict[str, Any]]:
    tech_skill = TechnicalAnalysisSkill()
    news_skill = NewsIntelligenceSkill()

    snapshot = await tech_skill.analyze_symbol(symbol=symbol, timeframe=timeframe, lookback="6mo")
    tech_score = _score_technical(snapshot)

    news = await news_skill.analyze(symbol)
    news_score = _score_news(news.get("sentiment") or {})

    # Fundamentals + risk placeholders (wire later to your real portfolio/broker state).
    fundamental_score = 55.0
    risk_score = 70.0

    price = float(snapshot.close)
    overall_score = _overall(tech_score, news_score, fundamental_score, risk_score)

    return price, {
        "technical_score": tech_score,
        "news_score": news_score,
        "fundamental_score": fundamental_score,
        "risk_score": risk_score,
        "overall_score": overall_score,
        "signal": str(snapshot.signal),
        "trend": str(snapshot.trend),
    }


async def main() -> None:
    logger.info("Watchlist executor started dashboard=%s interval_sec=%s", DASHBOARD_URL, CHECK_INTERVAL_SECONDS)

    while True:
        post_status("online", "Polling watchlist", 0)
        try:
            items: List[Dict[str, Any]] = _get_json(f"{DASHBOARD_URL}/api/watchlist", timeout=20) or []
            active = [i for i in items if str(i.get("status") or "active") != "removed"]
            logger.info("Loaded watchlist count=%s", len(active))

            for idx, item in enumerate(active, start=1):
                symbol = str(item.get("symbol") or "").upper().strip()
                if not symbol:
                    continue
                timeframe = str(item.get("timeframe") or "1d")
                strategy_id = str(item.get("strategy_id") or "default")

                post_status("processing", f"Analyzing {symbol}", int(idx / max(len(active), 1) * 100))
                price, scores = await _analyze_symbol(symbol, timeframe)

                # Simple rule: only emit BUY when technical says buy_bias AND overall_score >= 60.
                is_buy = str(scores.get("signal", "")).lower() == "buy_bias" and float(scores.get("overall_score") or 0) >= 60.0
                if is_buy:
                    payload = {
                        "symbol": symbol,
                        "signal": "buy",
                        "strategy_id": strategy_id,
                        "price": float(price or 0.0),
                        "technical_score": float(scores["technical_score"]),
                        "news_score": float(scores["news_score"]),
                        "fundamental_score": float(scores["fundamental_score"]),
                        "risk_score": float(scores["risk_score"]),
                        "overall_score": float(scores["overall_score"]),
                    }
                    try:
                        res = _post_json(f"{DASHBOARD_URL}/alerts/buy-signal", payload, timeout=20)
                        logger.info("Posted BUY signal symbol=%s status=%s", symbol, res.get("status"))
                    except Exception as exc:
                        logger.warning("Failed posting signal symbol=%s error=%s", symbol, exc)
                else:
                    logger.info("No buy signal symbol=%s signal=%s overall=%.1f", symbol, scores.get("signal"), float(scores.get("overall_score") or 0))

            post_status("idle", "Cycle complete", 100)
        except Exception as exc:
            logger.error("Executor error: %s", exc, exc_info=True)
            post_status("error", str(exc), 0)

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())


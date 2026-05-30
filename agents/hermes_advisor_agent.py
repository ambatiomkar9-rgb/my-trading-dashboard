"""Hermes advisor agent.

Uses Hermes Agent (installed in Ubuntu/WSL) to produce self-learning notes that
help improve strategy rules over time.

Workflow:
1) Poll cloud dashboard for pending signals.
2) Ask Hermes for a short "lesson" + suggested rule improvements.
3) Store the lesson in ReflexionMemory (SQLite) so other agents can retrieve it.
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
from typing import Any, Dict, Optional, Set

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
        logging.FileHandler(str(_LOGS_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

from trading_system.integrations.hermes_client import HermesClient
from trading_system.memory.reflexion_memory import ReflexionEntry, ReflexionMemoryRepository

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://my-trading-dashboard-8.onrender.com").rstrip("/")
POLL_SECONDS = int(os.getenv("HERMES_POLL_INTERVAL", "30"))
DB_PATH = os.getenv("TRADING_LOCAL_SQLITE_PATH", str((_PKG_DIR / "data" / "trading_system.db").resolve()))


def _safe_json(resp: urllib.response.addinfourl) -> Any:
    body = resp.read().decode("utf-8")
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
        "agent_id": "hermes_advisor",
        "status": status,
        "task": task,
        "progress": progress,
        "timestamp": datetime.now().isoformat(),
    }
    try:
        _post_json(f"{DASHBOARD_URL}/agent-status", payload, timeout=10)
    except Exception:
        pass


def _prompt_for_signal(signal: Dict[str, Any]) -> str:
    symbol = str(signal.get("symbol") or "UNKNOWN")
    price = float(signal.get("signal_price") or 0.0)
    tech = float(signal.get("technical_score") or 0.0)
    news = float(signal.get("news_score") or 0.0)
    fund = float(signal.get("fundamental_score") or 0.0)
    risk = float(signal.get("risk_score") or 0.0)
    overall = float(signal.get("overall_score") or 0.0)
    strategy_id = str(signal.get("strategy_id") or "default")
    return (
        "You are a trading assistant helping improve a rule-based strategy.\n"
        "Given this pending BUY signal, produce:\n"
        "1) Decision: APPROVE or SKIP\n"
        "2) 3 bullet reasons\n"
        "3) A short 'lesson learned' sentence to improve future signals\n"
        "4) Suggested rule tweaks (as plain text, not code)\n\n"
        f"Symbol: {symbol}\n"
        f"Strategy: {strategy_id}\n"
        f"Price: {price}\n"
        f"Scores (0-100): technical={tech}, news={news}, fundamentals={fund}, risk={risk}, overall={overall}\n\n"
        "Keep it concise."
    )


class HermesAdvisorAgent:
    def __init__(self, hermes: HermesClient, repo: ReflexionMemoryRepository) -> None:
        self.hermes = hermes
        self.repo = repo
        self.seen: Set[str] = set()

    async def run_once(self) -> Optional[Dict[str, Any]]:
        signals = _get_json(f"{DASHBOARD_URL}/api/signals/pending", timeout=20) or []
        if not isinstance(signals, list) or not signals:
            return None

        # Only process one per cycle to keep CPU/network low.
        signal = signals[0]
        sid = str(signal.get("id") or "")
        if not sid or sid in self.seen:
            return None

        prompt = _prompt_for_signal(signal)
        answer = await asyncio.to_thread(self.hermes.query, prompt)
        if not answer or answer.startswith("HERMES_ERROR") or answer == "HERMES_TIMEOUT":
            raise RuntimeError(answer or "Hermes returned empty response")

        symbol = str(signal.get("symbol") or "UNKNOWN")
        strategy_id = str(signal.get("strategy_id") or "default")
        entry = ReflexionEntry(
            symbol=symbol,
            strategy_id=strategy_id,
            outcome="advice",
            pnl=0.0,
            lesson=answer[:2000],
            created_at=datetime.utcnow(),
        )
        row_id = await self.repo.add_entry(entry)
        self.seen.add(sid)
        return {"signal_id": sid, "reflexion_id": row_id, "symbol": symbol}


async def main() -> None:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    repo = ReflexionMemoryRepository(sqlite_path=DB_PATH)
    await repo.initialize()
    agent = HermesAdvisorAgent(hermes=HermesClient(), repo=repo)

    while True:
        try:
            post_status("online", "Waiting for pending signals", 0)
            res = await agent.run_once()
            if res:
                post_status("idle", f"Learned from signal {res['signal_id']}", 100)
                logger.info("Hermes advice stored signal_id=%s reflexion_id=%s", res["signal_id"], res["reflexion_id"])
            else:
                post_status("idle", "No pending signals", 100)
        except Exception as exc:
            logger.error("Hermes advisor error: %s", exc, exc_info=True)
            post_status("error", str(exc), 0)
        await asyncio.sleep(POLL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())


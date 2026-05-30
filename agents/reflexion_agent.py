"""Reflexion/learning agent for continuous system improvement."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from trading_system.memory.reflexion_memory import ReflexionEntry, ReflexionMemoryRepository
from trading_system.memory.vector_memory import VectorMemory

logger = logging.getLogger(__name__)


class ReflexionAgent:
    """Derives and stores lessons after outcomes."""

    def __init__(self, repo: ReflexionMemoryRepository, vector_memory: VectorMemory) -> None:
        self.repo = repo
        self.vector_memory = vector_memory

    async def reflect_trade(
        self,
        symbol: str,
        strategy_id: str,
        pnl: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create and persist one reflexion entry."""
        context = context or {}
        if pnl > 0:
            outcome = "win"
            lesson = "Conditions aligned with strategy edge; preserve setup filters."
        elif pnl < 0:
            outcome = "loss"
            lesson = "Loss likely from regime mismatch; tighten filters or reduce size."
        else:
            outcome = "flat"
            lesson = "No edge realized; avoid overtrading this setup."

        entry = ReflexionEntry(
            symbol=symbol,
            strategy_id=strategy_id,
            outcome=outcome,
            pnl=pnl,
            lesson=lesson,
            created_at=datetime.now(timezone.utc),
        )
        row_id = await self.repo.add_entry(entry)
        vec_text = f"{symbol} {strategy_id} {outcome} {lesson} context={context}"
        self.vector_memory.upsert(record_id=f"reflexion:{row_id}", text=vec_text, metadata={"symbol": symbol})
        logger.info("Reflexion saved symbol=%s pnl=%.2f", symbol, pnl)
        return {"id": row_id, "symbol": symbol, "strategy_id": strategy_id, "outcome": outcome, "lesson": lesson}

    async def latest(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Return recent reflexion items and summary."""
        lessons = await self.repo.recent_lessons(symbol=symbol, limit=10)
        summary = await self.repo.summarize(symbol=symbol)
        return {"lessons": lessons, "summary": summary}

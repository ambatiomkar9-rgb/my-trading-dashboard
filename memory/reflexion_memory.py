"""Reflexion memory store for continuous learning feedback."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiosqlite

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ReflexionEntry:
    """Learning record generated after trade outcomes."""

    symbol: str
    strategy_id: str
    outcome: str
    pnl: float
    lesson: str
    created_at: datetime


class ReflexionMemoryRepository:
    """Simple SQLite repository for reflexion entries."""

    def __init__(self, sqlite_path: str) -> None:
        self.sqlite_path = sqlite_path

    async def initialize(self) -> None:
        """Create schema."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS reflexions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    strategy_id TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    pnl REAL NOT NULL,
                    lesson TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_reflexions_symbol_strategy
                ON reflexions(symbol, strategy_id)
                """
            )
            await db.commit()

    async def add_entry(self, entry: ReflexionEntry) -> int:
        """Insert reflexion entry."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO reflexions (symbol, strategy_id, outcome, pnl, lesson, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.symbol,
                    entry.strategy_id,
                    entry.outcome,
                    entry.pnl,
                    entry.lesson,
                    entry.created_at.isoformat(),
                ),
            )
            await db.commit()
            row_id = int(cursor.lastrowid)
            logger.info("Reflexion logged id=%s symbol=%s", row_id, entry.symbol)
            return row_id

    async def recent_lessons(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent lessons globally or by symbol."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            if symbol:
                cursor = await db.execute(
                    """
                    SELECT symbol, strategy_id, outcome, pnl, lesson, created_at
                    FROM reflexions
                    WHERE symbol = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (symbol, limit),
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT symbol, strategy_id, outcome, pnl, lesson, created_at
                    FROM reflexions
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            rows = await cursor.fetchall()
            return [
                {
                    "symbol": row[0],
                    "strategy_id": row[1],
                    "outcome": row[2],
                    "pnl": row[3],
                    "lesson": row[4],
                    "created_at": row[5],
                }
                for row in rows
            ]

    async def summarize(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Return simple learning summary stats."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            if symbol:
                cursor = await db.execute(
                    """
                    SELECT
                        COUNT(*) AS total,
                        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS wins,
                        SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) AS losses,
                        COALESCE(AVG(pnl), 0) AS avg_pnl
                    FROM reflexions
                    WHERE symbol = ?
                    """,
                    (symbol,),
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT
                        COUNT(*) AS total,
                        SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS wins,
                        SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) AS losses,
                        COALESCE(AVG(pnl), 0) AS avg_pnl
                    FROM reflexions
                    """
                )
            row = await cursor.fetchone()
            return {
                "total": int(row[0] or 0),
                "wins": int(row[1] or 0),
                "losses": int(row[2] or 0),
                "avg_pnl": float(row[3] or 0.0),
            }

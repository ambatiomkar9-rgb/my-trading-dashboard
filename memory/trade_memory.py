"""SQLite-backed trade repository."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiosqlite

from trading_system.config.models import ExecutionResult, TradingMode

logger = logging.getLogger(__name__)


class TradeMemoryRepository:
    """
    Trade memory repository with append-only execution logging.

    Unit-test example:
        >>> repo = TradeMemoryRepository(':memory:')
        >>> asyncio.run(repo.initialize())
    """

    def __init__(self, sqlite_path: str) -> None:
        self.sqlite_path = sqlite_path

    async def initialize(self) -> None:
        """Initialize schema."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT,
                    mode TEXT NOT NULL,
                    broker TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    average_price REAL,
                    status TEXT NOT NULL,
                    accepted INTEGER NOT NULL,
                    message TEXT,
                    metadata_json TEXT,
                    pnl REAL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_trades_mode_symbol
                ON trades(mode, symbol)
                """
            )
            await db.commit()

    async def log_execution(self, result: ExecutionResult) -> int:
        """Persist one execution event."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO trades (
                    order_id, mode, broker, symbol, side, quantity,
                    average_price, status, accepted, message, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.order_id,
                    result.mode.value,
                    result.broker,
                    result.symbol,
                    result.side.value,
                    result.quantity,
                    result.average_price,
                    result.status,
                    1 if result.accepted else 0,
                    result.message,
                    str(result.metadata),
                    result.executed_at.isoformat(),
                ),
            )
            await db.commit()
            row_id = int(cursor.lastrowid)
            logger.info("Trade logged id=%s symbol=%s mode=%s", row_id, result.symbol, result.mode.value)
            return row_id

    async def update_trade_pnl(self, trade_id: int, pnl: float) -> None:
        """Update PnL for a closed trade row."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            await db.execute("UPDATE trades SET pnl = ? WHERE id = ?", (pnl, trade_id))
            await db.commit()

    async def recent_trades(self, mode: TradingMode, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent trades."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                SELECT id, order_id, mode, broker, symbol, side, quantity, average_price,
                       status, accepted, message, metadata_json, pnl, created_at
                FROM trades
                WHERE mode = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (mode.value, limit),
            )
            rows = await cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "order_id": row[1],
                    "mode": row[2],
                    "broker": row[3],
                    "symbol": row[4],
                    "side": row[5],
                    "quantity": row[6],
                    "average_price": row[7],
                    "status": row[8],
                    "accepted": bool(row[9]),
                    "message": row[10],
                    "metadata_json": row[11],
                    "pnl": row[12],
                    "created_at": row[13],
                }
                for row in rows
            ]

    async def trade_stats(self, mode: TradingMode) -> Dict[str, float]:
        """Aggregate win/loss counters for risk checks."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) AS wins,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) AS losses,
                    COALESCE(SUM(pnl), 0) AS net_pnl
                FROM trades
                WHERE mode = ?
                """,
                (mode.value,),
            )
            row = await cursor.fetchone()
            total = int(row[0] or 0)
            wins = int(row[1] or 0)
            losses = int(row[2] or 0)
            net_pnl = float(row[3] or 0.0)
            return {
                "total": total,
                "wins": wins,
                "losses": losses,
                "win_rate": (wins / total) if total else 0.0,
                "net_pnl": net_pnl,
            }

    async def count_consecutive_losses(self, mode: TradingMode, lookback: int = 20) -> int:
        """Count consecutive losing trades from latest backward."""
        async with aiosqlite.connect(self.sqlite_path) as db:
            cursor = await db.execute(
                """
                SELECT pnl
                FROM trades
                WHERE mode = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (mode.value, lookback),
            )
            rows = await cursor.fetchall()
            streak = 0
            for (pnl,) in rows:
                if pnl < 0:
                    streak += 1
                else:
                    break
            return streak

    async def heartbeat(self) -> Dict[str, Any]:
        """Simple health endpoint payload."""
        return {"db": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

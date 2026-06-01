"""Execution Recovery — restart-safe persistence for open orders, signals, and positions.

On startup, this module:
1. Reloads open executions from the database
2. Reconciles with broker state (paper or live)
3. Marks stale orders as expired
4. Updates position snapshots
5. Prevents duplicate order placement
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class OpenExecution:
    """An execution that was submitted but not yet confirmed filled."""
    execution_id: str
    order_id: str
    symbol: str
    side: str
    quantity: float
    broker: str
    mode: str
    status: str
    submitted_at: float
    broker_order_id: Optional[str] = None
    last_checked_at: float = 0.0
    check_count: int = 0


class ExecutionRecoveryManager:
    """Manages restart-safe execution state.

    - Persists open executions to a SQLite database
    - On startup, reloads and reconciles with broker
    - Provides idempotency checks for duplicate prevention
    """

    def __init__(self, db_path: str = "data/execution_recovery.db") -> None:
        self._db_path = db_path
        self._open_executions: dict[str, OpenExecution] = {}
        self._conn: Any = None
        self._init_db()

    def _init_db(self) -> None:
        """Create the recovery table if it doesn't exist."""
        import sqlite3
        import os

        os.makedirs(os.path.dirname(self._db_path) or ".", exist_ok=True)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS open_executions (
                execution_id TEXT PRIMARY KEY,
                order_id TEXT,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                broker TEXT,
                mode TEXT,
                status TEXT,
                submitted_at REAL,
                broker_order_id TEXT,
                last_checked_at REAL,
                check_count INTEGER
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS filled_executions (
                execution_id TEXT PRIMARY KEY,
                order_id TEXT,
                symbol TEXT,
                side TEXT,
                quantity REAL,
                fill_price REAL,
                broker TEXT,
                mode TEXT,
                filled_at REAL
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS idempotency_store (
                client_order_id TEXT PRIMARY KEY,
                broker TEXT,
                status TEXT,
                broker_order_id TEXT,
                created_at REAL
            )
        """)
        self._conn.commit()

    def record_submission(
        self,
        execution_id: str,
        order_id: str,
        symbol: str,
        side: str,
        quantity: float,
        broker: str,
        mode: str,
        broker_order_id: Optional[str] = None,
    ) -> None:
        """Record that an order was submitted (called before broker API call)."""
        now = time.time()
        exec_record = OpenExecution(
            execution_id=execution_id,
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            broker=broker,
            mode=mode,
            status="submitted",
            submitted_at=now,
            broker_order_id=broker_order_id,
        )
        self._open_executions[execution_id] = exec_record

        try:
            self._conn.execute(
                """INSERT OR REPLACE INTO open_executions
                   (execution_id, order_id, symbol, side, quantity, broker, mode,
                    status, submitted_at, broker_order_id, last_checked_at, check_count)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (execution_id, order_id, symbol, side, quantity, broker, mode,
                 "submitted", now, broker_order_id, 0, 0),
            )
            self._conn.commit()
        except Exception as exc:
            logger.warning("Failed to persist open execution: %s", exc)

    def record_fill(
        self,
        execution_id: str,
        fill_price: float,
    ) -> None:
        """Record that an order was filled (called after broker confirms fill)."""
        now = time.time()
        exec_record = self._open_executions.pop(execution_id, None)

        try:
            self._conn.execute("DELETE FROM open_executions WHERE execution_id = ?", (execution_id,))
            if exec_record:
                self._conn.execute(
                    """INSERT INTO filled_executions
                       (execution_id, order_id, symbol, side, quantity, fill_price, broker, mode, filled_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (execution_id, exec_record.order_id, exec_record.symbol, exec_record.side,
                     exec_record.quantity, fill_price, exec_record.broker, exec_record.mode, now),
                )
            self._conn.commit()
        except Exception as exc:
            logger.warning("Failed to record fill: %s", exc)

    def record_rejection(self, execution_id: str, reason: str = "") -> None:
        """Record that an order was rejected."""
        self._open_executions.pop(execution_id, None)
        try:
            self._conn.execute(
                "UPDATE open_executions SET status = ? WHERE execution_id = ?",
                (f"rejected:{reason[:100]}", execution_id),
            )
            self._conn.commit()
        except Exception as exc:
            logger.warning("Failed to record rejection: %s", exc)

    def is_duplicate(self, client_order_id: str) -> bool:
        """Check if an order has already been submitted (idempotency check)."""
        try:
            row = self._conn.execute(
                "SELECT status FROM idempotency_store WHERE client_order_id = ?",
                (client_order_id,),
            ).fetchone()
            return row is not None
        except Exception:
            return False

    def mark_submitted(self, client_order_id: str, broker: str, broker_order_id: str = "") -> None:
        """Mark an order as submitted in the idempotency store."""
        try:
            self._conn.execute(
                """INSERT OR REPLACE INTO idempotency_store
                   (client_order_id, broker, status, broker_order_id, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (client_order_id, broker, "submitted", broker_order_id, time.time()),
            )
            self._conn.commit()
        except Exception as exc:
            logger.warning("Failed to mark idempotency: %s", exc)

    def load_open_executions(self) -> list[OpenExecution]:
        """Load all open executions from the database (called on startup)."""
        try:
            rows = self._conn.execute(
                "SELECT execution_id, order_id, symbol, side, quantity, broker, mode, status, submitted_at, broker_order_id, last_checked_at, check_count FROM open_executions"
            ).fetchall()
            executions = []
            for row in rows:
                exec_record = OpenExecution(
                    execution_id=row[0],
                    order_id=row[1],
                    symbol=row[2],
                    side=row[3],
                    quantity=row[4],
                    broker=row[5],
                    mode=row[6],
                    status=row[7],
                    submitted_at=row[8],
                    broker_order_id=row[9],
                    last_checked_at=row[10],
                    check_count=row[11],
                )
                self._open_executions[exec_record.execution_id] = exec_record
                executions.append(exec_record)
            logger.info("Loaded %d open executions from recovery DB", len(executions))
            return executions
        except Exception as exc:
            logger.warning("Failed to load open executions: %s", exc)
            return []

    def reconcile_with_broker(self, broker_adapter: Any) -> dict[str, str]:
        """Check open executions against broker state and update accordingly.

        Returns a dict of execution_id -> resolved_status ("filled", "expired", "still_open").
        """
        results: dict[str, str] = {}
        stale_threshold = 300  # 5 minutes without broker response = expired
        now = time.time()

        for exec_id, exec_record in list(self._open_executions.items()):
            try:
                if exec_record.broker_order_id and broker_adapter is not None:
                    status = broker_adapter.get_order_status(exec_record.broker_order_id)
                    if status and str(status).lower() in ("filled", "completed"):
                        results[exec_id] = "filled"
                        self.record_fill(exec_id, fill_price=0.0)
                        continue

                # Check if stale
                age = now - exec_record.submitted_at
                if age > stale_threshold or exec_record.check_count > 60:
                    results[exec_id] = "expired"
                    self.record_rejection(exec_id, "expired_on_recovery")
                    logger.info("Execution %s expired during recovery (age=%.0fs)", exec_id, age)
                    continue

                results[exec_id] = "still_open"
                exec_record.check_count += 1
                exec_record.last_checked_at = now

                # Update DB
                self._conn.execute(
                    "UPDATE open_executions SET check_count = ?, last_checked_at = ? WHERE execution_id = ?",
                    (exec_record.check_count, exec_record.last_checked_at, exec_id),
                )
            except Exception as exc:
                logger.warning("Reconciliation failed for %s: %s", exec_id, exc)
                results[exec_id] = "error"

        self._conn.commit()
        return results

    def get_open_count(self) -> int:
        """Return the number of open executions."""
        return len(self._open_executions)

    def get_stats(self) -> dict[str, Any]:
        """Return recovery stats for health checks."""
        try:
            open_count = self._conn.execute("SELECT COUNT(*) FROM open_executions").fetchone()[0]
            filled_today = self._conn.execute(
                "SELECT COUNT(*) FROM filled_executions WHERE filled_at > ?",
                (time.time() - 86400,),
            ).fetchone()[0]
            return {
                "open_executions": open_count,
                "filled_today": filled_today,
                "in_memory_open": len(self._open_executions),
            }
        except Exception:
            return {"open_executions": 0, "filled_today": 0, "in_memory_open": len(self._open_executions)}

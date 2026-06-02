"""Execution Recovery — restart-safe persistence for open orders, signals, and positions.

On startup, this module:
1. Reloads open executions from the database
2. Reconciles with broker state (paper or live)
3. Marks stale orders as expired
4. Updates position snapshots
5. Prevents duplicate order placement

Uses SQLAlchemy (Supabase PostgreSQL) instead of raw SQLite for persistence across redeploys.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.exc import IntegrityError

from backend.database import Base, SessionLocal

logger = logging.getLogger(__name__)


class OpenExecutionRow(Base):
    __tablename__ = "execution_recovery_open"

    execution_id = Column(String(128), primary_key=True)
    order_id = Column(String(128))
    symbol = Column(String(32))
    side = Column(String(16))
    quantity = Column(Float)
    broker = Column(String(32))
    mode = Column(String(16))
    status = Column(String(64))
    submitted_at = Column(Float)
    broker_order_id = Column(String(128), nullable=True)
    last_checked_at = Column(Float, default=0.0)
    check_count = Column(Integer, default=0)


class FilledExecutionRow(Base):
    __tablename__ = "execution_recovery_filled"

    execution_id = Column(String(128), primary_key=True)
    order_id = Column(String(128))
    symbol = Column(String(32))
    side = Column(String(16))
    quantity = Column(Float)
    fill_price = Column(Float)
    broker = Column(String(32))
    mode = Column(String(16))
    filled_at = Column(Float)


class IdempotencyRow(Base):
    __tablename__ = "execution_recovery_idempotency"

    client_order_id = Column(String(128), primary_key=True)
    broker = Column(String(32))
    status = Column(String(64))
    broker_order_id = Column(String(128))
    created_at = Column(Float)


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
    """Manages restart-safe execution state using SQLAlchemy (Supabase PostgreSQL)."""

    def __init__(self) -> None:
        self._open_executions: dict[str, OpenExecution] = {}
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        from backend.database import engine
        Base.metadata.create_all(engine, checkfirst=True)

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

        session = SessionLocal()
        try:
            session.add(OpenExecutionRow(
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
                last_checked_at=0,
                check_count=0,
            ))
            session.commit()
        except Exception as exc:
            session.rollback()
            logger.warning("Failed to persist open execution: %s", exc)
        finally:
            session.close()

    def record_fill(self, execution_id: str, fill_price: float) -> None:
        now = time.time()
        exec_record = self._open_executions.pop(execution_id, None)

        session = SessionLocal()
        try:
            session.query(OpenExecutionRow).filter(
                OpenExecutionRow.execution_id == execution_id
            ).delete()
            if exec_record:
                session.add(FilledExecutionRow(
                    execution_id=execution_id,
                    order_id=exec_record.order_id,
                    symbol=exec_record.symbol,
                    side=exec_record.side,
                    quantity=exec_record.quantity,
                    fill_price=fill_price,
                    broker=exec_record.broker,
                    mode=exec_record.mode,
                    filled_at=now,
                ))
            session.commit()
        except Exception as exc:
            session.rollback()
            logger.warning("Failed to record fill: %s", exc)
        finally:
            session.close()

    def record_rejection(self, execution_id: str, reason: str = "") -> None:
        self._open_executions.pop(execution_id, None)
        session = SessionLocal()
        try:
            row = session.query(OpenExecutionRow).filter(
                OpenExecutionRow.execution_id == execution_id
            ).first()
            if row:
                row.status = f"rejected:{reason[:100]}"
                session.commit()
        except Exception as exc:
            session.rollback()
            logger.warning("Failed to record rejection: %s", exc)
        finally:
            session.close()

    def is_duplicate(self, client_order_id: str) -> bool:
        session = SessionLocal()
        try:
            row = session.query(IdempotencyRow).filter(
                IdempotencyRow.client_order_id == client_order_id
            ).first()
            return row is not None
        except Exception:
            return False
        finally:
            session.close()

    def mark_submitted(self, client_order_id: str, broker: str, broker_order_id: str = "") -> None:
        session = SessionLocal()
        try:
            existing = session.query(IdempotencyRow).filter(
                IdempotencyRow.client_order_id == client_order_id
            ).first()
            if existing:
                existing.broker = broker
                existing.status = "submitted"
                existing.broker_order_id = broker_order_id
                existing.created_at = time.time()
            else:
                session.add(IdempotencyRow(
                    client_order_id=client_order_id,
                    broker=broker,
                    status="submitted",
                    broker_order_id=broker_order_id,
                    created_at=time.time(),
                ))
            session.commit()
        except Exception as exc:
            session.rollback()
            logger.warning("Failed to mark idempotency: %s", exc)
        finally:
            session.close()

    def load_open_executions(self) -> list[OpenExecution]:
        session = SessionLocal()
        try:
            rows = session.query(OpenExecutionRow).all()
            executions = []
            for row in rows:
                exec_record = OpenExecution(
                    execution_id=row.execution_id,
                    order_id=row.order_id or "",
                    symbol=row.symbol or "",
                    side=row.side or "",
                    quantity=row.quantity or 0,
                    broker=row.broker or "",
                    mode=row.mode or "",
                    status=row.status or "submitted",
                    submitted_at=row.submitted_at or 0,
                    broker_order_id=row.broker_order_id,
                    last_checked_at=row.last_checked_at or 0,
                    check_count=row.check_count or 0,
                )
                self._open_executions[exec_record.execution_id] = exec_record
                executions.append(exec_record)
            logger.info("Loaded %d open executions from recovery DB", len(executions))
            return executions
        except Exception as exc:
            logger.warning("Failed to load open executions: %s", exc)
            return []
        finally:
            session.close()

    def reconcile_with_broker(self, broker_adapter: Any) -> dict[str, str]:
        results: dict[str, str] = {}
        stale_threshold = 300
        now = time.time()

        for exec_id, exec_record in list(self._open_executions.items()):
            try:
                if exec_record.broker_order_id and broker_adapter is not None:
                    status = broker_adapter.get_order_status(exec_record.broker_order_id)
                    if status and str(status).lower() in ("filled", "completed"):
                        results[exec_id] = "filled"
                        self.record_fill(exec_id, fill_price=0.0)
                        continue

                age = now - exec_record.submitted_at
                if age > stale_threshold or exec_record.check_count > 60:
                    results[exec_id] = "expired"
                    self.record_rejection(exec_id, "expired_on_recovery")
                    logger.info("Execution %s expired during recovery (age=%.0fs)", exec_id, age)
                    continue

                results[exec_id] = "still_open"
                exec_record.check_count += 1
                exec_record.last_checked_at = now

                session = SessionLocal()
                try:
                    row = session.query(OpenExecutionRow).filter(
                        OpenExecutionRow.execution_id == exec_id
                    ).first()
                    if row:
                        row.check_count = exec_record.check_count
                        row.last_checked_at = exec_record.last_checked_at
                        session.commit()
                except Exception:
                    session.rollback()
                finally:
                    session.close()

            except Exception as exc:
                logger.warning("Reconciliation failed for %s: %s", exec_id, exc)
                results[exec_id] = "error"

        return results

    def get_open_count(self) -> int:
        return len(self._open_executions)

    def get_stats(self) -> dict[str, Any]:
        session = SessionLocal()
        try:
            open_count = session.query(OpenExecutionRow).count()
            filled_today = session.query(FilledExecutionRow).filter(
                FilledExecutionRow.filled_at > time.time() - 86400
            ).count()
            return {
                "open_executions": open_count,
                "filled_today": filled_today,
                "in_memory_open": len(self._open_executions),
            }
        except Exception:
            return {"open_executions": 0, "filled_today": 0, "in_memory_open": len(self._open_executions)}
        finally:
            session.close()

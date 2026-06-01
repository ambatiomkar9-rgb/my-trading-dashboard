"""Strategy memory for self-learning from trade outcomes.

Stores lessons learned from Hermes strategy analysis and trade results.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from backend.database import Base, SessionLocal

logger = logging.getLogger(__name__)


class StrategyLesson(Base):
    """Model for strategy lessons learned from trade outcomes."""

    __tablename__ = "strategy_lessons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy_id = Column(String(64), index=True, nullable=True)
    strategy_name = Column(String(255), nullable=True)
    symbol = Column(String(32), index=True, nullable=True)
    outcome = Column(String(32), nullable=True)  # win, loss, flat, advice
    pnl = Column(Float, default=0.0)
    lesson_text = Column(Text, nullable=True)
    metrics_json = Column(Text, nullable=True)
    source = Column(String(32), default="hermes")  # hermes, fallback, manual
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class StrategyLessonRepository:
    """Repository for strategy lesson persistence."""

    def store_lesson(
        self,
        strategy_id: Optional[str],
        strategy_name: Optional[str],
        symbol: Optional[str],
        outcome: str,
        pnl: float,
        lesson_text: str,
        metrics: Optional[dict] = None,
        source: str = "hermes",
    ) -> None:
        """Store a lesson learned from a trade outcome."""
        session = SessionLocal()
        try:
            lesson = StrategyLesson(
                strategy_id=strategy_id,
                strategy_name=strategy_name,
                symbol=symbol,
                outcome=outcome,
                pnl=pnl,
                lesson_text=lesson_text,
                metrics_json=json.dumps(metrics) if metrics else None,
                source=source,
                created_at=datetime.now(timezone.utc),
            )
            session.add(lesson)
            session.commit()
            logger.info(
                "Stored lesson for %s/%s: %s (pnl=%.2f)",
                strategy_name,
                symbol,
                outcome,
                pnl,
            )
        except Exception as exc:
            session.rollback()
            logger.error("Failed to store lesson: %s", exc)
        finally:
            session.close()

    def get_lessons(
        self,
        symbol: Optional[str] = None,
        strategy_id: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Retrieve recent lessons, optionally filtered by symbol or strategy."""
        session = SessionLocal()
        try:
            query = session.query(StrategyLesson).order_by(
                StrategyLesson.created_at.desc()
            )
            if symbol:
                query = query.filter(StrategyLesson.symbol == symbol.upper())
            if strategy_id:
                query = query.filter(StrategyLesson.strategy_id == strategy_id)
            rows = query.limit(limit).all()
            return [
                {
                    "id": row.id,
                    "strategy_id": row.strategy_id,
                    "strategy_name": row.strategy_name,
                    "symbol": row.symbol,
                    "outcome": row.outcome,
                    "pnl": row.pnl,
                    "lesson_text": row.lesson_text,
                    "metrics": json.loads(row.metrics_json) if row.metrics_json else None,
                    "source": row.source,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                for row in rows
            ]
        finally:
            session.close()

    def get_lessons_summary(self, symbol: Optional[str] = None) -> dict[str, Any]:
        """Get aggregated lesson statistics."""
        session = SessionLocal()
        try:
            query = session.query(StrategyLesson)
            if symbol:
                query = query.filter(StrategyLesson.symbol == symbol.upper())
            rows = query.all()

            total = len(rows)
            wins = sum(1 for r in rows if r.outcome == "win")
            losses = sum(1 for r in rows if r.outcome == "loss")
            total_pnl = sum(r.pnl or 0 for r in rows)
            win_rate = (wins / total * 100) if total > 0 else 0

            return {
                "total_lessons": total,
                "wins": wins,
                "losses": losses,
                "win_rate": round(win_rate, 2),
                "total_pnl": round(total_pnl, 2),
                "recent_lessons": [
                    {"outcome": r.outcome, "lesson": r.lesson_text, "pnl": r.pnl}
                    for r in rows[:10]
                ],
            }
        finally:
            session.close()

    def get_lesson_texts(self, symbol: Optional[str] = None, limit: int = 10) -> list[str]:
        """Get lesson texts for Hermes prompt injection."""
        lessons = self.get_lessons(symbol=symbol, limit=limit)
        return [l["lesson_text"] for l in lessons if l.get("lesson_text")]

    def cleanup_old_lessons(self, days: int = 90) -> int:
        """Remove lessons older than N days."""
        session = SessionLocal()
        try:
            from datetime import timedelta

            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            old = (
                session.query(StrategyLesson)
                .filter(StrategyLesson.created_at < cutoff)
                .all()
            )
            count = len(old)
            for lesson in old:
                session.delete(lesson)
            session.commit()
            return count
        except Exception as exc:
            session.rollback()
            logger.error("Failed to cleanup old lessons: %s", exc)
            return 0
        finally:
            session.close()

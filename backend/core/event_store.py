"""Event Store — persistent event log with replay, TTL, and dead-letter queue.

Uses SQLAlchemy (Supabase PostgreSQL) for persistence across redeploys.

Features:
  - store_event / get_events (existing)
  - replay_events: replay events from a given timestamp
  - dead_letter: store events that failed processing
  - cleanup: remove events older than TTL
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.exc import OperationalError

from backend.database import Base, SessionLocal

logger = logging.getLogger(__name__)

DEFAULT_TTL_DAYS = int(os.getenv("EVENT_TTL_DAYS", "30"))


class EventRow(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, index=True)
    event_type = Column(String(100), index=True)
    payload = Column(Text)
    timestamp = Column(DateTime, index=True)
    source = Column(String(100))
    status = Column(String(20), default="active")  # active | dead


class EventDeadLetterRow(Base):
    __tablename__ = "events_dead_letter"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), index=True)
    event_type = Column(String(100), index=True)
    payload = Column(Text)
    timestamp = Column(DateTime)
    source = Column(String(100))
    error = Column(Text)
    dead_at = Column(DateTime)


@dataclass(slots=True)
class EventStore:
    """Persistent event store with replay, TTL, and dead-letter support."""

    ttl_days: int = DEFAULT_TTL_DAYS
    engine: Any = field(init=False, repr=False)
    Session: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        from backend.database import engine as default_engine, SessionLocal as DefaultSession
        self.engine = default_engine
        self.Session = DefaultSession
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        try:
            EventRow.__table__.create(self.engine, checkfirst=True)
            EventDeadLetterRow.__table__.create(self.engine, checkfirst=True)
        except Exception as exc:
            logger.warning("Could not ensure event tables: %s", exc)

    def store_event(self, event_type: str, payload: Dict[str, Any], source: str = "system") -> str:
        event_id = uuid.uuid4().hex
        session = self.Session()
        try:
            session.add(EventRow(
                event_id=event_id,
                event_type=event_type,
                payload=json.dumps(payload),
                timestamp=datetime.utcnow(),
                source=source,
                status="active",
            ))
            session.commit()
            return event_id
        except Exception as exc:
            session.rollback()
            logger.warning("store_event failed: %s", exc)
            return ""
        finally:
            session.close()

    def get_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        session = self.Session()
        try:
            q = session.query(EventRow).filter(EventRow.status == "active")
            if event_type:
                q = q.filter(EventRow.event_type == event_type)
            rows = q.order_by(EventRow.timestamp.desc()).limit(limit).all()
            return [
                {
                    "event_id": r.event_id,
                    "event_type": r.event_type,
                    "payload": json.loads(r.payload or "{}"),
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                    "source": r.source,
                }
                for r in rows
            ]
        except Exception as exc:
            logger.warning("get_events failed: %s", exc)
            return []
        finally:
            session.close()

    def replay_events(
        self,
        from_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """Replay events from a given timestamp (oldest first)."""
        session = self.Session()
        try:
            q = session.query(EventRow).filter(EventRow.status == "active")
            if from_time:
                q = q.filter(EventRow.timestamp >= from_time)
            if event_type:
                q = q.filter(EventRow.event_type == event_type)
            rows = q.order_by(EventRow.timestamp.asc()).limit(limit).all()
            return [
                {
                    "event_id": r.event_id,
                    "event_type": r.event_type,
                    "payload": json.loads(r.payload or "{}"),
                    "timestamp": r.timestamp.isoformat() if r.timestamp else None,
                    "source": r.source,
                }
                for r in rows
            ]
        except Exception as exc:
            logger.warning("replay_events failed: %s", exc)
            return []
        finally:
            session.close()

    def send_to_dead_letter(
        self,
        event_id: str,
        event_type: str,
        payload: Dict[str, Any],
        source: str,
        error: str,
    ) -> None:
        """Move a failed event to the dead-letter queue."""
        session = self.Session()
        try:
            session.add(EventDeadLetterRow(
                event_id=event_id,
                event_type=event_type,
                payload=json.dumps(payload),
                timestamp=datetime.utcnow(),
                source=source,
                error=error[:1000],
                dead_at=datetime.utcnow(),
            ))
            session.query(EventRow).filter(EventRow.event_id == event_id).update({"status": "dead"})
            session.commit()
        except Exception as exc:
            session.rollback()
            logger.warning("send_to_dead_letter failed: %s", exc)
        finally:
            session.close()

    def get_dead_letters(self, limit: int = 50) -> List[Dict[str, Any]]:
        session = self.Session()
        try:
            rows = session.query(EventDeadLetterRow).order_by(
                EventDeadLetterRow.dead_at.desc()
            ).limit(limit).all()
            return [
                {
                    "event_id": r.event_id,
                    "event_type": r.event_type,
                    "payload": json.loads(r.payload or "{}"),
                    "error": r.error,
                    "dead_at": r.dead_at.isoformat() if r.dead_at else None,
                }
                for r in rows
            ]
        except Exception:
            return []
        finally:
            session.close()

    def cleanup_expired(self) -> int:
        """Remove events older than TTL. Returns count of removed events."""
        session = self.Session()
        try:
            cutoff = datetime.utcnow() - timedelta(days=self.ttl_days)
            count = session.query(EventRow).filter(EventRow.timestamp < cutoff).delete()
            session.query(EventDeadLetterRow).filter(
                EventDeadLetterRow.dead_at < cutoff
            ).delete()
            session.commit()
            if count:
                logger.info("Cleaned up %d expired events (older than %d days)", count, self.ttl_days)
            return count
        except Exception as exc:
            session.rollback()
            logger.warning("cleanup_expired failed: %s", exc)
            return 0
        finally:
            session.close()


def build_event_store(default_db_url: str = "") -> EventStore:
    return EventStore()

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, index=True)
    event_type = Column(String(100), index=True)
    payload = Column(Text)
    timestamp = Column(DateTime, index=True)
    source = Column(String(100))


@dataclass(slots=True)
class EventStore:
    """
    Persistent event store (SQLite/Postgres depending on EVENT_DB_URL).

    Default uses the same DATABASE_URL as the dashboard so everything is in one place.
    """

    db_url: str
    # With slots=True, we must declare any attributes we set in __post_init__.
    engine: Any = field(init=False, repr=False)
    Session: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        connect_args: Dict[str, Any] = {}
        if self.db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        self.engine = create_engine(self.db_url, connect_args=connect_args, pool_pre_ping=True)
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(self.engine)

    def store_event(self, event_type: str, payload: Dict[str, Any], source: str = "system") -> str:
        event_id = uuid.uuid4().hex
        session = self.Session()
        try:
            ev = Event(
                event_id=event_id,
                event_type=event_type,
                payload=json.dumps(payload),
                timestamp=datetime.utcnow(),
                source=source,
            )
            session.add(ev)
            session.commit()
            return event_id
        finally:
            session.close()

    def get_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        session = self.Session()
        try:
            q = session.query(Event)
            if event_type:
                q = q.filter(Event.event_type == event_type)
            rows = q.order_by(Event.timestamp.desc()).limit(limit).all()
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
        finally:
            session.close()


def build_event_store(default_db_url: str) -> EventStore:
    db_url = os.getenv("EVENT_DB_URL", "").strip() or default_db_url
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return EventStore(db_url=db_url)

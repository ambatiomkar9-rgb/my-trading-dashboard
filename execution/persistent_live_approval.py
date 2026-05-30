"""SQLite-backed live approval tickets shared across agent processes.

Why:
- The original LiveApprovalManager keeps tickets in memory, so approvals made in
  one process (BossAgent) are invisible to another (TradeExecutionAgent).
- This manager persists tickets in a local SQLite DB so multiple processes can
  create/approve/consume the same ticket safely.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from trading_system.config.models import OrderRequest, TradingMode

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LiveApprovalTicket:
    ticket_id: str
    fingerprint: str
    order_preview: Dict[str, Any]
    requested_by: str
    requested_at: datetime
    expires_at: datetime
    approved: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    consumed: bool = False
    consumed_at: Optional[datetime] = None


class PersistentLiveApprovalManager:
    """DB-backed implementation of the live approval workflow."""

    def __init__(self, sqlite_path: str, ttl_seconds: int = 300) -> None:
        self.sqlite_path = str(Path(sqlite_path))
        self.ttl_seconds = ttl_seconds
        self._lock = asyncio.Lock()
        self._ensure_db()

    def fingerprint(self, order: OrderRequest) -> str:
        payload = {
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": round(float(order.quantity), 10),
            "mode": order.mode.value,
            "broker": order.broker.lower(),
            "order_type": order.order_type.value,
            "limit_price": order.limit_price,
            "stop_loss": order.stop_loss,
            "take_profit": order.take_profit,
            "leverage": round(float(order.leverage), 8),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    async def create_ticket(self, order: OrderRequest, requested_by: str = "operator") -> Dict[str, Any]:
        if order.mode != TradingMode.LIVE:
            raise ValueError("Live approval tickets can only be created for live orders.")
        now = datetime.now(timezone.utc)
        ticket_id = f"LIVEAP-{uuid.uuid4().hex[:12]}"
        ticket = LiveApprovalTicket(
            ticket_id=ticket_id,
            fingerprint=self.fingerprint(order),
            order_preview=order.model_dump(mode="json"),
            requested_by=requested_by,
            requested_at=now,
            expires_at=now + timedelta(seconds=self.ttl_seconds),
        )
        async with self._lock:
            self._upsert(ticket)
        return self._ticket_dict(ticket)

    async def approve_ticket(self, ticket_id: str, approved_by: str = "supervisor") -> Dict[str, Any]:
        async with self._lock:
            ticket = self._get(ticket_id)
            if not ticket:
                raise ValueError("Approval ticket not found.")
            if self._expired(ticket):
                raise ValueError("Approval ticket expired.")
            if ticket.consumed:
                raise ValueError("Approval ticket already consumed.")
            ticket.approved = True
            ticket.approved_by = approved_by
            ticket.approved_at = datetime.now(timezone.utc)
            self._upsert(ticket)
            return self._ticket_dict(ticket)

    async def consume_for_order(self, ticket_id: str, order: OrderRequest) -> bool:
        expected = self.fingerprint(order)
        async with self._lock:
            ticket = self._get(ticket_id)
            if not ticket:
                return False
            if self._expired(ticket) or ticket.consumed or not ticket.approved:
                return False
            if not hmac.compare_digest(ticket.fingerprint, expected):
                return False
            ticket.consumed = True
            ticket.consumed_at = datetime.now(timezone.utc)
            self._upsert(ticket)
            return True

    async def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            ticket = self._get(ticket_id)
            return self._ticket_dict(ticket) if ticket else None

    async def cleanup_expired(self) -> int:
        removed = 0
        now = datetime.now(timezone.utc)
        async with self._lock:
            conn = self._connect()
            try:
                cur = conn.execute("DELETE FROM live_approval_tickets WHERE expires_at <= ?", (now.isoformat(),))
                removed = int(cur.rowcount or 0)
                conn.commit()
            finally:
                conn.close()
        return removed

    def _ensure_db(self) -> None:
        Path(self.sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        conn = self._connect()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS live_approval_tickets (
                    ticket_id TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL,
                    order_preview_json TEXT NOT NULL,
                    requested_by TEXT NOT NULL,
                    requested_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    approved INTEGER NOT NULL DEFAULT 0,
                    approved_by TEXT,
                    approved_at TEXT,
                    consumed INTEGER NOT NULL DEFAULT 0,
                    consumed_at TEXT
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS ix_live_approval_expires ON live_approval_tickets(expires_at)")
            conn.commit()
        finally:
            conn.close()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.sqlite_path, timeout=30)

    def _upsert(self, ticket: LiveApprovalTicket) -> None:
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO live_approval_tickets (
                    ticket_id, fingerprint, order_preview_json, requested_by, requested_at, expires_at,
                    approved, approved_by, approved_at, consumed, consumed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(ticket_id) DO UPDATE SET
                    fingerprint=excluded.fingerprint,
                    order_preview_json=excluded.order_preview_json,
                    requested_by=excluded.requested_by,
                    requested_at=excluded.requested_at,
                    expires_at=excluded.expires_at,
                    approved=excluded.approved,
                    approved_by=excluded.approved_by,
                    approved_at=excluded.approved_at,
                    consumed=excluded.consumed,
                    consumed_at=excluded.consumed_at
                """,
                (
                    ticket.ticket_id,
                    ticket.fingerprint,
                    json.dumps(ticket.order_preview, ensure_ascii=True, separators=(",", ":")),
                    ticket.requested_by,
                    ticket.requested_at.isoformat(),
                    ticket.expires_at.isoformat(),
                    1 if ticket.approved else 0,
                    ticket.approved_by,
                    ticket.approved_at.isoformat() if ticket.approved_at else None,
                    1 if ticket.consumed else 0,
                    ticket.consumed_at.isoformat() if ticket.consumed_at else None,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _get(self, ticket_id: str) -> Optional[LiveApprovalTicket]:
        conn = self._connect()
        try:
            row = conn.execute(
                """
                SELECT
                    ticket_id, fingerprint, order_preview_json, requested_by, requested_at, expires_at,
                    approved, approved_by, approved_at, consumed, consumed_at
                FROM live_approval_tickets
                WHERE ticket_id = ?
                """,
                (ticket_id,),
            ).fetchone()
            if not row:
                return None
            order_preview = json.loads(row[2])
            return LiveApprovalTicket(
                ticket_id=row[0],
                fingerprint=row[1],
                order_preview=order_preview,
                requested_by=row[3],
                requested_at=datetime.fromisoformat(row[4]),
                expires_at=datetime.fromisoformat(row[5]),
                approved=bool(row[6]),
                approved_by=row[7],
                approved_at=datetime.fromisoformat(row[8]) if row[8] else None,
                consumed=bool(row[9]),
                consumed_at=datetime.fromisoformat(row[10]) if row[10] else None,
            )
        finally:
            conn.close()

    def _expired(self, ticket: LiveApprovalTicket) -> bool:
        return ticket.expires_at <= datetime.now(timezone.utc)

    def _ticket_dict(self, ticket: LiveApprovalTicket) -> Dict[str, Any]:
        return {
            "ticket_id": ticket.ticket_id,
            "fingerprint": ticket.fingerprint,
            "requested_by": ticket.requested_by,
            "requested_at": ticket.requested_at.isoformat(),
            "expires_at": ticket.expires_at.isoformat(),
            "approved": ticket.approved,
            "approved_by": ticket.approved_by,
            "approved_at": ticket.approved_at.isoformat() if ticket.approved_at else None,
            "consumed": ticket.consumed,
            "consumed_at": ticket.consumed_at.isoformat() if ticket.consumed_at else None,
            "order_preview": ticket.order_preview,
        }


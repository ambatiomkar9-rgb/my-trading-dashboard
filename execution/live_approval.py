"""Human-supervised one-time live order approvals."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from trading_system.config.models import OrderRequest, TradingMode

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class LiveApprovalTicket:
    """Approval ticket bound to one live order fingerprint."""

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


class LiveApprovalManager:
    """Manages issue/approve/consume lifecycle for live order tickets."""

    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._tickets: Dict[str, LiveApprovalTicket] = {}
        self._lock = asyncio.Lock()

    def fingerprint(self, order: OrderRequest) -> str:
        """Create stable order fingerprint used by approval tickets."""
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
        """Create one approval ticket for a live order."""
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
            self._tickets[ticket_id] = ticket
        return self._ticket_dict(ticket)

    async def approve_ticket(self, ticket_id: str, approved_by: str = "supervisor") -> Dict[str, Any]:
        """Approve a pending ticket."""
        async with self._lock:
            ticket = self._tickets.get(ticket_id)
            if not ticket:
                raise ValueError("Approval ticket not found.")
            if self._expired(ticket):
                raise ValueError("Approval ticket expired.")
            if ticket.consumed:
                raise ValueError("Approval ticket already consumed.")
            ticket.approved = True
            ticket.approved_by = approved_by
            ticket.approved_at = datetime.now(timezone.utc)
            return self._ticket_dict(ticket)

    async def consume_for_order(self, ticket_id: str, order: OrderRequest) -> bool:
        """Consume ticket if approved and order fingerprint matches exactly."""
        expected = self.fingerprint(order)
        async with self._lock:
            ticket = self._tickets.get(ticket_id)
            if not ticket:
                return False
            if self._expired(ticket) or ticket.consumed or not ticket.approved:
                return False
            if not hmac.compare_digest(ticket.fingerprint, expected):
                return False
            ticket.consumed = True
            ticket.consumed_at = datetime.now(timezone.utc)
            return True

    async def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ticket by id."""
        async with self._lock:
            ticket = self._tickets.get(ticket_id)
            if not ticket:
                return None
            return self._ticket_dict(ticket)

    async def cleanup_expired(self) -> int:
        """Delete expired tickets to bound memory."""
        removed = 0
        now = datetime.now(timezone.utc)
        async with self._lock:
            stale = [k for k, v in self._tickets.items() if v.expires_at <= now]
            for key in stale:
                self._tickets.pop(key, None)
                removed += 1
        return removed

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

"""Reusable event handlers for logging and state updates."""

from __future__ import annotations

import logging
from typing import Awaitable, Callable

from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import Event, EventType
from trading_system.memory.global_state import GlobalState
from trading_system.memory.trade_memory import TradeMemoryRepository

logger = logging.getLogger(__name__)


async def log_all_events(event: Event) -> None:
    """Structured event logging handler."""
    logger.info("Event=%s source=%s payload=%s", event.event_type.value, event.source, event.payload)


async def on_kill_switch(event: Event) -> None:
    """Escalation logging for kill switch triggers."""
    logger.error("KILL SWITCH TRIGGERED: %s", event.payload)


def register_default_handlers(
    bus: AsyncEventBus,
    state: GlobalState,
    trade_memory: TradeMemoryRepository,
) -> None:
    """Register default handlers used by orchestration layer."""

    async def trade_executed_handler(event: Event) -> None:
        logger.info("Trade executed event received: %s", event.payload.get("order_id"))

    async def position_closed_handler(event: Event) -> None:
        logger.info("Position closed: %s", event.payload.get("symbol"))

    bus.subscribe(EventType.SIGNAL_DETECTED, log_all_events)
    bus.subscribe(EventType.RISK_APPROVED, log_all_events)
    bus.subscribe(EventType.RISK_REJECTED, log_all_events)
    bus.subscribe(EventType.TRADE_EXECUTED, trade_executed_handler)
    bus.subscribe(EventType.POSITION_CLOSED, position_closed_handler)
    bus.subscribe(EventType.WHALE_ALERT, log_all_events)
    bus.subscribe(EventType.MACRO_ALERT, log_all_events)
    bus.subscribe(EventType.KILL_SWITCH_TRIGGERED, on_kill_switch)

"""Async event bus with retry-safe dispatch."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Awaitable, Callable, DefaultDict, Dict, List, Optional

from trading_system.events.event_types import Event, EventType

logger = logging.getLogger(__name__)

EventHandler = Callable[[Event], Awaitable[None]]


class AsyncEventBus:
    """
    Event bus for decoupled agent communication.

    Unit-test example:
        >>> bus = AsyncEventBus()
        >>> async def handler(event): pass
        >>> bus.subscribe(EventType.SYSTEM_HEARTBEAT, handler)
    """

    def __init__(self, queue_size: int = 10000, worker_count: int = 4) -> None:
        self._handlers: DefaultDict[EventType, List[EventHandler]] = defaultdict(list)
        self._queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=queue_size)
        self._worker_count = worker_count
        self._workers: List[asyncio.Task[None]] = []
        self._running = False

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Register event handler."""
        self._handlers[event_type].append(handler)
        logger.debug("Subscribed handler=%s event=%s", handler.__name__, event_type.value)

    async def publish(self, event: Event) -> None:
        """Publish event to queue with backpressure."""
        if not self._running:
            logger.warning("Event bus not running; event queued lazily event=%s", event.event_type.value)
        await self._queue.put(event)

    async def start(self) -> None:
        """Start worker tasks."""
        if self._running:
            return
        self._running = True
        self._workers = [asyncio.create_task(self._worker_loop(i)) for i in range(self._worker_count)]
        logger.info("Event bus started workers=%s", self._worker_count)

    async def stop(self) -> None:
        """Stop worker tasks gracefully."""
        if not self._running:
            return
        self._running = False
        for _ in self._workers:
            await self._queue.put(
                Event(
                    event_type=EventType.SYSTEM_HEARTBEAT,
                    source="event_bus.stop",
                    payload={"stop": True},
                )
            )
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("Event bus stopped")

    async def _worker_loop(self, worker_id: int) -> None:
        """Background event dispatcher loop."""
        while True:
            event = await self._queue.get()
            try:
                if not self._running and event.payload.get("stop"):
                    return
                await self._dispatch(event)
            except Exception:
                logger.exception("Event dispatch failed event=%s worker=%s", event.event_type.value, worker_id)
            finally:
                self._queue.task_done()

    async def _dispatch(self, event: Event) -> None:
        """Dispatch event to all handlers concurrently."""
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            logger.debug("No handlers for event=%s", event.event_type.value)
            return
        await asyncio.gather(*(handler(event) for handler in handlers), return_exceptions=False)

    def stats(self) -> Dict[str, int]:
        """Queue metrics."""
        return {"queue_size": self._queue.qsize(), "worker_count": len(self._workers)}

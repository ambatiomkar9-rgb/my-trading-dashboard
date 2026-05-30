"""WebSocket manager for streaming events to dashboard clients."""

from __future__ import annotations

import json
import logging
from typing import List, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from trading_system.events.event_bus import AsyncEventBus
from trading_system.events.event_types import Event, EventType

logger = logging.getLogger(__name__)


class WebSocketBroadcaster:
    """Broadcast bus events to connected websocket clients."""

    def __init__(self, event_bus: AsyncEventBus) -> None:
        self.event_bus = event_bus
        self._clients: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)
        logger.info("WebSocket client connected count=%s", len(self._clients))

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)
        logger.info("WebSocket client disconnected count=%s", len(self._clients))

    async def broadcast(self, event: Event) -> None:
        if not self._clients:
            return
        dead: List[WebSocket] = []
        message = json.dumps(event.as_dict(), default=str)
        for ws in self._clients:
            try:
                await ws.send_text(message)
            except Exception:  # noqa: BLE001
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    def register_bus_handlers(self) -> None:
        """Subscribe broadcaster to all event types."""
        for event_type in EventType:
            self.event_bus.subscribe(event_type, self.broadcast)


def create_websocket_router(broadcaster: WebSocketBroadcaster) -> APIRouter:
    """Create websocket router."""
    router = APIRouter()

    @router.websocket("/ws/events")
    async def events_websocket(websocket: WebSocket) -> None:
        await broadcaster.connect(websocket)
        try:
            while True:
                # Keep connection alive by reading messages (ignored).
                await websocket.receive_text()
        except WebSocketDisconnect:
            broadcaster.disconnect(websocket)
        except Exception:
            broadcaster.disconnect(websocket)

    return router

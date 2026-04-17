"""
WebSocket Connection Manager
==============================
Handles the pool of active WebSocket connections.
Provides typed broadcast methods with per-connection error isolation
and automatic pruning of dead connections.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import List

from fastapi import WebSocket
from fastapi.websockets import WebSocketState


class ConnectionManager:
    """
    Manages all active WebSocket connections.

    Features:
      - Isolated per-connection error handling (one bad client won't block others).
      - Automatic removal of stale/closed connections.
      - Typed broadcast_event() with structured JSON payloads.
      - Connection tracking with timestamps for diagnostics.
    """

    def __init__(self) -> None:
        self._connections: List[WebSocket] = []
        self._connected_at: dict[int, datetime] = {}

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection and register it."""
        await websocket.accept()
        self._connections.append(websocket)
        self._connected_at[id(websocket)] = datetime.now(timezone.utc)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a closed WebSocket from the pool."""
        self._connections = [c for c in self._connections if c is not websocket]
        self._connected_at.pop(id(websocket), None)

    @property
    def active_count(self) -> int:
        """Returns the number of currently tracked connections."""
        return len(self._connections)

    async def broadcast_event(self, event_type: str, payload: dict) -> None:
        """
        Broadcast a structured JSON event to all active connections.

        The message envelope is:
            { "type": "<event_type>", "timestamp": "<ISO-8601>", ...payload }

        Dead connections are silently pruned from the pool.

        Args:
            event_type: String identifier for the event (e.g., 'AI_STATE_TICK').
            payload: Arbitrary JSON-serialisable data to include in the message.
        """
        message = {
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **payload,
        }

        dead: List[WebSocket] = []

        # Fan out concurrently for low latency
        send_tasks = []
        live_connections = list(self._connections)

        for ws in live_connections:
            if ws.client_state == WebSocketState.CONNECTED:
                send_tasks.append(self._safe_send(ws, message, dead))

        if send_tasks:
            await asyncio.gather(*send_tasks)

        # Prune dead connections
        for ws in dead:
            self.disconnect(ws)

    async def _safe_send(
        self,
        websocket: WebSocket,
        message: dict,
        dead: List[WebSocket],
    ) -> None:
        """
        Attempt to send a message to a single client.
        Marks the connection as dead on any exception.
        """
        try:
            await websocket.send_json(message)
        except Exception:
            dead.append(websocket)


# Module-level singleton
manager = ConnectionManager()

# MODULE: WebSocket connection manager for decoupling the Voice Engine.
"""Manages WebSocket connections for real-time inter-process communication."""

from __future__ import annotations

import logging
from typing import List

from fastapi import WebSocket

from src.common.logging_utils import configure_logging
from src.voice.protocol import VoiceStatus, VoiceStatusEvent

LOGGER = configure_logging(__name__)

class ConnectionManager:
    """Manages active WebSocket connections to the Brain API."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.current_voice_status = VoiceStatus.IDLE

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        LOGGER.info("WebSocket client connected. Total clients: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            LOGGER.info("WebSocket client disconnected. Total clients: %d", len(self.active_connections))

    async def broadcast_status(self, status: str, trace_id: str | None = None, detail: str | None = None):
        """Send a status update to all connected UI clients."""
        self.current_voice_status = status
        message = VoiceStatusEvent(status=status, trace_id=trace_id, detail=detail).to_json()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                LOGGER.error("Error broadcasting status: %s", e)

    def get_voice_state(self) -> dict:
        """Return current voice connection and state information."""
        return {
            "connections": len(self.active_connections),
            "status": self.current_voice_status,
        }

# Global manager instance
manager = ConnectionManager()

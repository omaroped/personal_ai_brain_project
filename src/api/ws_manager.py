# MODULE: WebSocket connection manager for decoupling the Voice Engine.
"""Manages WebSocket connections for real-time inter-process communication."""

from __future__ import annotations

import json
import logging
from typing import List

from fastapi import WebSocket, WebSocketDisconnect

from src.common.logging_utils import configure_logging

LOGGER = configure_logging(__name__)

class ConnectionManager:
    """Manages active WebSocket connections to the Brain API."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        LOGGER.info("WebSocket client connected. Total clients: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            LOGGER.info("WebSocket client disconnected. Total clients: %d", len(self.active_connections))

    async def broadcast_status(self, status: str):
        """Send a status update to all connected UI clients."""
        message = json.dumps({"type": "status", "status": status})
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                LOGGER.error("Error broadcasting status: %s", e)

# Global manager instance
manager = ConnectionManager()

#!/usr/bin/env python3
"""
WebSocket Manager - Real-time Intelligence Broadcasting
======================================================

Manages WebSocket connections for live Chennai tech intelligence updates.
"""

import logging
import json
from typing import Set, Dict, Any
from datetime import datetime

from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time intelligence updates"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"🔌 WebSocket connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"🔌 WebSocket disconnected. Total connections: {len(self.active_connections)}")
        
    async def broadcast_update(self, intelligence_data: Dict[str, Any]):
        """Broadcast intelligence update to all connected clients"""
        
        if not self.active_connections:
            return
            
        message = {
            "type": "intelligence_update",
            "data": intelligence_data,
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"❌ Failed to send to WebSocket client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
            
        if self.active_connections:
            logger.info(f"📡 Broadcasted update to {len(self.active_connections)} clients")
    
    def connection_count(self) -> int:
        """Get current connection count"""
        return len(self.active_connections)
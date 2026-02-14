"""Internal event bus for asynchronous processing."""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from app.db.redis import get_redis


class EventBus:
    """Redis-backed simple event bus for internal orchestration."""
    
    STREAM_NAME = "xether:events"

    @staticmethod
    async def publish(
        event_type: str,
        payload: Dict[str, Any],
        resource_id: Optional[int] = None
    ) -> str:
        """
        Publish an event to the internal stream.
        Returns the message ID.
        """
        redis = await get_redis()
        event_data = {
            "type": event_type,
            "payload": json.dumps(payload),
            "resource_id": str(resource_id) if resource_id else "",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Using Redis Streams for persistence and multiple consumer support
        message_id = await redis.xadd(EventBus.STREAM_NAME, event_data)
        return str(message_id)


# Global instance
events = EventBus()

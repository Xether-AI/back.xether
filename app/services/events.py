"""Internal event bus for asynchronous processing."""

import json
from datetime import datetime
from typing import Any, Dict, Optional
import logging

# Import the new NATS event bus
from app.core.events import get_event_bus

logger = logging.getLogger(__name__)


class EventBus:
    """
    Event bus wrapper for backward compatibility.
    Now uses NATS instead of Redis Streams.
    """
    
    @staticmethod
    async def publish(
        event_type: str,
        payload: Dict[str, Any],
        resource_id: Optional[int] = None
    ) -> str:
        """
        Publish an event to NATS.
        
        Args:
            event_type: Event type (e.g., "pipeline.executed")
            payload: Event payload
            resource_id: Optional resource ID
            
        Returns:
            Message ID (for compatibility, returns "ok")
        """
        # Get NATS event bus
        nats_bus = await get_event_bus()
        
        # Convert event_type to NATS subject format
        # If it already starts with a known prefix, use it as is
        if event_type.startswith(("backend.", "pipeline.")):
            subject = event_type
        else:
            # "pipeline.executed" -> "backend.pipeline.executed"
            subject = f"backend.{event_type}"
        
        # Prepare event data
        event_data = {
            "type": event_type,
            "payload": payload,
            "resource_id": resource_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish to NATS
        await nats_bus.publish(subject, event_data)
        logger.debug(f"Published event {event_type} to {subject}")
        
        return "ok"


# Global instance for backward compatibility
events = EventBus()

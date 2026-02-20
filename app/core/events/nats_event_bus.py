"""NATS-based event bus implementation."""

import asyncio
import json
from typing import Any, Callable, Dict, Optional
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig
import logging

logger = logging.getLogger(__name__)


class NATSEventBus:
    """NATS JetStream-backed event bus for distributed event processing."""
    
    def __init__(self, servers: list[str]):
        """
        Initialize NATS event bus.
        
        Args:
            servers: List of NATS server URLs (e.g., ["nats://localhost:4222"])
        """
        self.servers = servers
        self.nc: Optional[NATS] = None
        self.js = None
        
    async def connect(self):
        """Connect to NATS server and setup JetStream."""
        try:
            self.nc = NATS()
            await self.nc.connect(servers=self.servers)
            self.js = self.nc.jetstream()
            
            # Create streams for different event types
            await self._setup_streams()
            logger.info(f"Connected to NATS at {self.servers}")
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            raise
    
    async def _setup_streams(self):
        """Setup JetStream streams for event persistence."""
        streams = [
            StreamConfig(name="BACKEND_EVENTS", subjects=["backend.>"]),
            StreamConfig(name="PIPELINE_EVENTS", subjects=["pipeline.>"]),
        ]
        
        for stream_config in streams:
            try:
                await self.js.add_stream(stream_config)
                logger.info(f"Created stream: {stream_config.name}")
            except Exception as e:
                # Stream might already exist
                logger.debug(f"Stream {stream_config.name} already exists or error: {e}")
    
    async def publish(self, subject: str, data: Dict[str, Any]):
        """
        Publish event to NATS.
        
        Args:
            subject: NATS subject (e.g., "backend.pipeline.executed")
            data: Event payload as dictionary
        """
        if not self.js:
            raise RuntimeError("NATS JetStream not initialized. Call connect() first.")
        
        try:
            payload = json.dumps(data).encode()
            ack = await self.js.publish(subject, payload)
            logger.debug(f"Published to {subject}: {data} (seq: {ack.seq})")
        except Exception as e:
            logger.error(f"Failed to publish to {subject}: {e}")
            raise
    
    async def subscribe(self, subject: str, callback: Callable, durable_name: str = None):
        """
        Subscribe to NATS subject with callback.
        
        Args:
            subject: NATS subject pattern (e.g., "pipeline.events.>")
            callback: Async function to handle messages
            durable_name: Optional durable consumer name for persistence
        """
        if not self.js:
            raise RuntimeError("NATS JetStream not initialized. Call connect() first.")
        
        async def message_handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await callback(data)
                await msg.ack()
            except Exception as e:
                logger.error(f"Error processing message from {subject}: {e}")
                # Don't ack on error - message will be redelivered
        
        try:
            if durable_name:
                await self.js.subscribe(subject, cb=message_handler, durable=durable_name)
            else:
                await self.js.subscribe(subject, cb=message_handler)
            logger.info(f"Subscribed to {subject}")
        except Exception as e:
            logger.error(f"Failed to subscribe to {subject}: {e}")
            raise
    
    async def close(self):
        """Close NATS connection."""
        if self.nc:
            await self.nc.close()
            logger.info("NATS connection closed")

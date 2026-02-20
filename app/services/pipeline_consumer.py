"""Pipeline event consumer for handling events from Main Pipeline service."""

import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.core.events import get_event_bus
from app.db.session import AsyncSessionLocal
from app.models.pipeline import PipelineExecution

logger = logging.getLogger(__name__)


async def handle_pipeline_event(data: dict):
    """
    Handle events from Main Pipeline.
    
    Expected event structure:
    {
        "execution_id": "uuid",
        "status": "completed" | "failed" | "running",
        "progress": 0.0-1.0,
        "error": "error message" (optional)
    }
    """
    execution_id = data.get("execution_id")
    status = data.get("status")
    error = data.get("error")
    progress = data.get("progress", 0.0)
    
    if not execution_id:
        logger.warning(f"Received pipeline event without execution_id: {data}")
        return
    
    logger.info(f"Processing pipeline event: execution_id={execution_id}, status={status}")
    
    # Update pipeline execution status in database
    async with AsyncSessionLocal() as db:
        try:
            # Find the execution
            result = await db.execute(
                select(PipelineExecution).where(PipelineExecution.id == execution_id)
            )
            execution = result.scalar_one_or_none()
            
            if not execution:
                logger.warning(f"Pipeline execution not found: {execution_id}")
                return
            
            # Update status
            if status == "completed":
                execution.status = "completed"
                execution.progress = 1.0
                logger.info(f"Pipeline execution {execution_id} completed successfully")
            
            elif status == "failed":
                execution.status = "failed"
                execution.error_message = error
                logger.error(f"Pipeline execution {execution_id} failed: {error}")
            
            elif status == "running":
                execution.status = "running"
                execution.progress = progress
                logger.debug(f"Pipeline execution {execution_id} progress: {progress}")
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error updating pipeline execution {execution_id}: {e}")
            await db.rollback()


async def start_consumer():
    """Start consuming pipeline events from NATS."""
    try:
        event_bus = await get_event_bus()
        
        # Subscribe to all pipeline events with durable consumer
        await event_bus.subscribe(
            "pipeline.events.>",
            handle_pipeline_event,
            durable_name="backend-pipeline-consumer"
        )
        
        logger.info("Pipeline event consumer started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start pipeline event consumer: {e}")
        raise

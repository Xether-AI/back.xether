"""Celery background tasks."""

import logging
from app.core.celery import celery_app
from app.db.session import AsyncSessionLocal
from app.services import audit as audit_service

logger = logging.getLogger(__name__)

@celery_app.task(name="process_audit_log")
def process_audit_log(user_id: int, action: str, resource_type: str, resource_id: int = None, meta_data: dict = None):
    """
    Process audit logs in the background.
    Note: Celery tasks are synchronous by nature in their execution block, 
    but we can run async code inside using an event loop if needed, 
    or just use synchronous DB sessions for simplicity in workers.
    """
    import asyncio
    
    async def _async_audit():
        async with AsyncSessionLocal() as db:
            await audit_service.create_audit_log(
                db,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                meta_data=meta_data
            )
            
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(_async_audit())
    else:
        loop.run_until_complete(_async_audit())

@celery_app.task(name="cleanup_old_executions")
def cleanup_old_executions():
    """Cleanup task for old pipeline execution records."""
    logger.info("Starting system cleanup...")
    # Implementation logic here
    logger.info("Cleanup complete.")

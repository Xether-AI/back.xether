"""Health check and diagnostic endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api import deps
from app.db.redis import get_redis
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/liveness")
@router.get("/")
async def liveness() -> dict[str, str]:
    """Basic health check for liveness probe."""
    return {"status": "healthy"}

@router.get("/readiness")
async def readiness(
    db: AsyncSession = Depends(deps.get_db)
) -> dict[str, str]:
    """Complete readiness check including DB and Redis."""
    health_status = {"status": "ready", "checks": {}}
    overall_ready = True
    
    # Check Database
    try:
        await db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "up"
    except Exception as e:
        logger.error(f"Readiness check failed for database: {e}")
        health_status["checks"]["database"] = "down"
        overall_ready = False
        
    # Check Redis
    try:
        redis = await get_redis()
        await redis.ping()
        health_status["checks"]["redis"] = "up"
    except Exception as e:
        logger.error(f"Readiness check failed for redis: {e}")
        health_status["checks"]["redis"] = "down"
        overall_ready = False
        
    if not overall_ready:
        health_status["status"] = "unready"
        # We don't necessarily raise an exception here so we can return the detailed json,
        # but k8s expects a non-200 status for failure.
        # Actually, let's just return a 503 if not ready.
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )

    return health_status

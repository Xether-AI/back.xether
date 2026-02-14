"""Redis connection management."""

from typing import Any

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()

# Redis connection pool
redis_pool: redis.ConnectionPool | None = None
redis_client: redis.Redis[Any] | None = None


async def init_redis() -> None:
    """Initialize Redis connection pool."""
    global redis_pool, redis_client

    redis_pool = redis.ConnectionPool.from_url(
        settings.redis_url_str,
        max_connections=settings.redis_max_connections,
        decode_responses=True,
    )
    redis_client = redis.Redis(connection_pool=redis_pool)


async def close_redis() -> None:
    """Close Redis connection pool."""
    global redis_pool, redis_client

    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()


async def get_redis() -> redis.Redis[Any]:
    """Get Redis client instance."""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return redis_client

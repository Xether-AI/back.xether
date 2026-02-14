"""Redis connection management."""

from typing import Any

import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()

# Redis connection pool
redis_pool: redis.ConnectionPool | None = None
redis_client: redis.Redis | None = None  # type: ignore[type-arg]


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


import json
from functools import wraps
from typing import Any, Callable, Optional


async def get_redis() -> redis.Redis:  # type: ignore[type-arg]
    """Get Redis client instance."""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return redis_client


def cache(
    key_prefix: str,
    expire: int = 3600,
    include_args: Optional[list[str]] = None,
) -> Callable[..., Any]:
    """
    Decorator to cache function results in Redis.
    :param key_prefix: Prefix for the cache key.
    :param expire: Expiration time in seconds.
    :param include_args: Specific argument names to include in the key. If None, all are used (dangerous).
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        import inspect
        sig = inspect.signature(func)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            if include_args:
                key_parts = [str(bound_args.arguments.get(a)) for a in include_args]
            else:
                # Fallback to all args except common complex objects
                key_parts = []
                for name, val in bound_args.arguments.items():
                    if name not in ["db", "session", "request", "background_tasks"]:
                        key_parts.append(f"{name}={val}")
            
            cache_key = f"cache:{key_prefix}:{':'.join(key_parts)}"
            
            redis = await get_redis()
            cached_val = await redis.get(cache_key)
            
            if cached_val:
                try:
                    return json.loads(cached_val)
                except Exception:
                    pass
            
            result = await func(*args, **kwargs)
            
            if result is not None:
                # Handle Pydantic models or SQLAlchemy models if needed
                # For now, assumes return is JSON serializable or has a __dict__
                try:
                    dump = json.dumps(result, default=str)
                    await redis.setex(cache_key, expire, dump)
                except Exception:
                    pass
            return result
        return wrapper
    return decorator



async def invalidate_cache(key_prefix: str, *args: Any) -> None:
    """Invalidate cache keys matching a prefix and arguments."""
    redis = await get_redis()
    if args:
        arg_str = ":".join([str(a) for a in args])
        # Match exactly OR as a prefix with a colon to avoid partial matches (e.g. 1 vs 10)
        keys = await redis.keys(f"cache:{key_prefix}:{arg_str}")
        keys_extra = await redis.keys(f"cache:{key_prefix}:{arg_str}:*")
        if keys_extra:
            keys.extend(keys_extra)
    else:
        keys = await redis.keys(f"cache:{key_prefix}:*")
        
    if keys:
        await redis.delete(*list(set(keys)))



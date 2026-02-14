"""Rate limiting utilities using Redis."""

import time
from fastapi import HTTPException, status, Request
from app.db.redis import get_redis
from app.core.config import get_settings

settings = get_settings()


async def check_rate_limit(request: Request, key_prefix: str = "rate_limit"):
    """Check rate limit for a request based on IP and key_prefix."""
    redis = await get_redis()
    client_ip = request.client.host if request.client else "unknown"
    key = f"{key_prefix}:{client_ip}"
    
    # Get current timestamp (minute)
    current_minute = int(time.time() / 60)
    redis_key = f"{key}:{current_minute}"
    
    # Increment counter
    count = await redis.incr(redis_key)
    if count == 1:
        # Set expiry for the key (1 minute)
        await redis.expire(redis_key, 60)
        
    if count > settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
        )

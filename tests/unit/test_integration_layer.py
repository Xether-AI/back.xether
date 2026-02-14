"""Tests for Redis caching and Event Bus."""

import pytest
import json
from unittest.mock import AsyncMock, patch
from app.db.redis import cache, invalidate_cache, get_redis
from app.services.events import events

@pytest.mark.asyncio
async def test_cache_decorator():
    """Test standard caching decorator behavior."""
    call_count = 0
    
    @cache("test_func", expire=10, include_args=["val"])
    async def mock_func(val: int, db=None):
        nonlocal call_count
        call_count += 1
        return {"result": val}
    
    # 1. First call (miss)
    res1 = await mock_func(1)
    assert res1 == {"result": 1}
    assert call_count == 1
    
    # 2. Second call (hit)
    res2 = await mock_func(1)
    assert res2 == {"result": 1}
    assert call_count == 1
    
    # 3. Third call different args (miss)
    res3 = await mock_func(2)
    assert res3 == {"result": 2}
    assert call_count == 2


@pytest.mark.asyncio
async def test_cache_invalidation():
    """Test custom cache invalidation."""
    call_count = 0
    
    @cache("inv_func", expire=10, include_args=["id"])
    async def mock_func(id: int):
        nonlocal call_count
        call_count += 1
        return {"id": id}
    
    await mock_func(100)
    assert call_count == 1
    
    await mock_func(100) # Hit
    assert call_count == 1
    
    await invalidate_cache("inv_func", 100)
    
    await mock_func(100) # Miss
    assert call_count == 2


@pytest.mark.asyncio
async def test_event_bus_publish():
    """Test publishing events to Redis Streams."""
    message_id = await events.publish("test.event", {"data": "hello"}, resource_id=123)
    assert message_id is not None
    
    redis = await get_redis()
    messages = await redis.xrange(events.STREAM_NAME)
    assert len(messages) > 0
    
    latest_payload = json.loads(messages[-1][1]["payload"])
    assert latest_payload["data"] == "hello"

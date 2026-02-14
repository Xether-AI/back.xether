"""Unit tests for API Key Service with mocking."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services import api_key as api_key_service
from app.models.base import APIKey

@pytest.mark.asyncio
async def test_create_api_key_unit():
    """Test creating a new API key."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    
    api_key = await api_key_service.create_api_key(mock_db, user_id=1, name="My Key")
    
    assert api_key.name == "My Key"
    assert api_key.user_id == 1
    assert api_key.key.startswith("xether_")
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_get_active_api_key_unit():
    """Test getting active API key."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_key = APIKey(id=1, key="test_key", is_active=True)
    mock_result.scalars.return_value.first.return_value = mock_key
    mock_db.execute.return_value = mock_result
    
    key = await api_key_service.get_active_api_key(mock_db, "test_key")
    
    assert key is not None
    assert key.key == "test_key"

@pytest.mark.asyncio
async def test_revoke_api_key_unit():
    """Test revoking an API key."""
    mock_db = AsyncMock()
    mock_key = APIKey(id=1, key="test_key", user_id=1, is_active=True)
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_key
    mock_db.execute.return_value = mock_result
    
    success = await api_key_service.revoke_api_key(mock_db, api_key_id=1, user_id=1)
    
    assert success is True
    assert mock_key.is_active is False
    assert mock_db.commit.called

"""Unit tests for User Service with mocking."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services import user as user_service
from app.models.base import User
from app.schemas.auth import UserCreate

@pytest.mark.asyncio
async def test_get_user_by_email_unit():
    """Test getting user by email with mocked DB."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    
    # Mocking SQLAlchemy result
    mock_user = User(id=1, email="test@example.com")
    mock_result.scalars.return_value.first.return_value = mock_user
    mock_db.execute.return_value = mock_result
    
    user = await user_service.get_user_by_email(mock_db, "test@example.com")
    
    assert user is not None
    assert user.email == "test@example.com"
    assert mock_db.execute.called

@pytest.mark.asyncio
async def test_create_user_unit():
    """Test creating a new user with mocked DB and password hashing."""
    mock_db = AsyncMock()
    # add and refresh are synchronous in SQLAlchemy
    mock_db.add = MagicMock()
    mock_db.refresh = AsyncMock() # refresh is async in AsyncSession
    
    user_in = UserCreate(email="new@example.com", password="password123")
    
    with patch("app.services.user.get_password_hash", return_value="hashed_pass"):
        user = await user_service.create_user(mock_db, user_in)
        
        assert user.email == "new@example.com"
        assert user.hashed_password == "hashed_pass"
        assert mock_db.add.called
        assert mock_db.commit.called
        assert mock_db.refresh.called

@pytest.mark.asyncio
async def test_get_user_by_id_cache_hit():
    """Test get_user_by_id with cache hit (skips DB)."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    
    # Mock redis to return cached JSON
    cached_user_json = '{"id": 1, "email": "cached@example.com", "hashed_password": "..."}'
    mock_redis.get.return_value = cached_user_json
    
    with patch("app.db.redis.get_redis", return_value=mock_redis):
        user = await user_service.get_user_by_id(mock_db, 1)
        
        assert user is not None
        assert user["id"] == 1
        assert user["email"] == "cached@example.com"
        assert not mock_db.execute.called
        assert mock_redis.get.called

@pytest.mark.asyncio
async def test_authenticate_user_success():
    """Test successful user authentication."""

    mock_db = AsyncMock()
    mock_user = User(email="test@example.com", hashed_password="hashed_password")
    
    with patch("app.services.user.get_user_by_email", return_value=mock_user), \
         patch("app.services.user.verify_password", return_value=True):
        
        user = await user_service.authenticate_user(mock_db, "test@example.com", "password123")
        
        assert user is not None
        assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_authenticate_user_fail_wrong_password():
    """Test failed authentication due to wrong password."""
    mock_db = AsyncMock()
    mock_user = User(email="test@example.com", hashed_password="hashed_password")
    
    with patch("app.services.user.get_user_by_email", return_value=mock_user), \
         patch("app.services.user.verify_password", return_value=False):
        
        user = await user_service.authenticate_user(mock_db, "test@example.com", "wrong_pass")
        assert user is None


@pytest.mark.asyncio
async def test_update_user_unit():
    """Test updating user details."""
    mock_db = AsyncMock()
    mock_user = User(id=1, email="old@example.com")
    from app.schemas.user import UserUpdate
    update_in = UserUpdate(email="new@example.com")
    
    with patch("app.services.user.invalidate_cache", new_callable=AsyncMock):
        updated = await user_service.update_user(mock_db, mock_user, update_in)
        assert updated.email == "new@example.com"
        assert mock_db.add.called
        assert mock_db.commit.called

@pytest.mark.asyncio
async def test_list_users_unit():
    """Test listing all users."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [User(id=1, email="u1@e.com")]
    mock_db.execute.return_value = mock_result
    
    users = await user_service.list_users(mock_db)
    assert len(users) == 1
    assert mock_db.execute.called


@pytest.mark.asyncio
async def test_get_user_by_id_cache_miss():
    """Test get_user_by_id with cache miss (calls DB)."""
    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_result = MagicMock()
    
    mock_user = User(id=1, email="test@example.com")
    mock_result.scalars.return_value.first.return_value = mock_user
    mock_db.execute.return_value = mock_result
    
    # Mock redis to return None (cache miss)
    mock_redis.get.return_value = None
    
    with patch("app.db.redis.get_redis", return_value=mock_redis):
        user = await user_service.get_user_by_id(mock_db, 1)
        
        assert user is not None
        assert user.id == 1
        assert mock_db.execute.called
        assert mock_redis.get.called
        assert mock_redis.setex.called

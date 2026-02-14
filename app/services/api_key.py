"""API Key services."""

import secrets
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import APIKey


async def create_api_key(
    db: AsyncSession, *, user_id: int, name: str, expires_at: Optional[datetime] = None
) -> APIKey:
    """Create a new API key."""
    # Generate a secure random key
    key = f"xether_{secrets.token_urlsafe(32)}"
    
    db_api_key = APIKey(
        key=key,
        name=name,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)
    return db_api_key


async def get_active_api_key(db: AsyncSession, key: str) -> Optional[APIKey]:
    """Get an active API key by its key string."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.key == key,
            APIKey.is_active == True
        )
    )
    db_api_key = result.scalars().first()
    
    if db_api_key and db_api_key.expires_at and db_api_key.expires_at < datetime.utcnow():
        return None
        
    return db_api_key


async def update_api_key_last_used(db: AsyncSession, api_key_id: int) -> None:
    """Update the last_used_at timestamp for an API key."""
    result = await db.execute(select(APIKey).where(APIKey.id == api_key_id))
    db_api_key = result.scalars().first()
    if db_api_key:
        db_api_key.last_used_at = datetime.utcnow()
        await db.commit()


async def list_user_api_keys(db: AsyncSession, user_id: int) -> List[APIKey]:
    """List all API keys for a user."""
    result = await db.execute(select(APIKey).where(APIKey.user_id == user_id))
    return list(result.scalars().all())


async def revoke_api_key(db: AsyncSession, api_key_id: int, user_id: int) -> bool:
    """Revoke (deactivate) an API key."""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id
        )
    )
    db_api_key = result.scalars().first()
    if db_api_key:
        db_api_key.is_active = False
        await db.commit()
        return True
    return False

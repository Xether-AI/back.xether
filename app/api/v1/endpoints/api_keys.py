"""API Key endpoints."""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.base import User
from app.services import api_key as api_key_service
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class APIKeyCreate(BaseModel):
    name: str
    expires_at: datetime | None = None


class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str | None = None  # Only shown on creation
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None = None
    expires_at: datetime | None = None

    class Config:
        from_attributes = True


@router.post("/", response_model=APIKeyResponse)
async def create_user_api_key(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    api_key_in: APIKeyCreate,
) -> Any:
    """Create a new API key for the current user."""
    return await api_key_service.create_api_key(
        db, user_id=current_user.id, name=api_key_in.name, expires_at=api_key_in.expires_at
    )


@router.get("/", response_model=List[APIKeyResponse])
async def list_user_api_keys(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all API keys for the current user."""
    api_keys = await api_key_service.list_user_api_keys(db, user_id=current_user.id)
    # Hide keys in list view
    for ak in api_keys:
        ak.key = None
    return api_keys


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_user_api_key(
    api_key_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Revoke an API key."""
    success = await api_key_service.revoke_api_key(
        db, api_key_id=api_key_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key not found",
        )
    return None

"""User management endpoints."""

from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.base import User
from app.schemas.auth import UserResponse
from app.schemas.user import UserUpdate
from app.services import user as user_service
from app.core.permissions import PermissionChecker, Role, Permission

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get current user's profile."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update current user's profile."""
    # Users can't change their own role or superuser status unless they are already superuser
    if not current_user.is_superuser:
        if user_in.role is not None or user_in.is_superuser is not None:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can update role or superuser status",
            )
    
    return await user_service.update_user(db, db_user=current_user, user_in=user_in)


@router.get("/", response_model=List[UserResponse], dependencies=[Depends(deps.get_current_superuser)])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List users (Admin only)."""
    return await user_service.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(deps.get_current_superuser)])
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """Get user by ID (Admin only)."""
    user = await user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

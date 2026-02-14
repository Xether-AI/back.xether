"""Authentication endpoints."""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.config import get_settings
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import Token, UserCreate, UserResponse, TokenData
from app.services import user as user_service

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate
) -> Any:
    """Register a new user."""
    user = await user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user = await user_service.create_user(db, user_in=user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = await user_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    
    return {
        "access_token": create_access_token(
            {"sub": user.email, "user_id": user.id}
        ),
        "refresh_token": create_refresh_token(
            {"sub": user.email, "user_id": user.id}
        ),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """Refresh access token."""
    payload = decode_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    token_data = TokenData(**payload)
    if token_data.type != "refresh" or token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
        
    user = await user_service.get_user_by_email(db, email=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
        
    return {
        "access_token": create_access_token(
            {"sub": user.email, "user_id": user.id}
        ),
        "refresh_token": create_refresh_token(
            {"sub": user.email, "user_id": user.id}
        ),
        "token_type": "bearer",
    }

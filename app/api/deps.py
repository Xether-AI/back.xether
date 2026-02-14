"""API dependencies."""

from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.models.base import User
from app.services import user as user_service
from app.services import api_key as api_key_service
from app.schemas.auth import TokenData

settings = get_settings()

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/login",
    auto_error=False
)

api_key_header = APIKeyHeader(
    name=settings.api_key_header,
    auto_error=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(reusable_oauth2),
    api_key: Optional[str] = Depends(api_key_header),
) -> User:
    """Get current authenticated user from JWT token or API Key."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Try API Key Authentication
    if api_key:
        db_api_key = await api_key_service.get_active_api_key(db, key=api_key)
        if db_api_key:
            await api_key_service.update_api_key_last_used(db, api_key_id=db_api_key.id)
            user = await user_service.get_user_by_id(db, user_id=db_api_key.user_id)
            if user:
                return user
        raise credentials_exception

    # 2. Try JWT Authentication
    if token:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
        
        token_data = TokenData(**payload)
        if token_data.sub is None or token_data.type != "access":
            raise credentials_exception
            
        user = await user_service.get_user_by_email(db, email=token_data.sub)
        if user is None:
            raise credentials_exception
            
        return user
        
    raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if the current user is a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user

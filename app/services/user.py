"""User service logic."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.base import User
from app.schemas.auth import UserCreate


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def update_user(db: AsyncSession, db_user: User, user_in: any) -> User:  # type: ignore[name-defined]
    """Update a user."""
    # Using Any for user_in because of circular import if we import UserUpdate here
    # and User service is often imported by schemas.
    # Alternatively, we can import inside the function.
    from app.schemas.user import UserUpdate
    
    if isinstance(user_in, dict):
        update_data = user_in
    else:
        update_data = user_in.model_dump(exclude_unset=True)
        
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """List users."""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


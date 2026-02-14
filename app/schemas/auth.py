"""Authentication and User schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """Token schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data schema."""
    sub: Optional[str] = None
    user_id: Optional[int] = None
    type: Optional[str] = None


class UserBase(BaseModel):
    """Base User schema."""
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)


class UserLogin(UserBase):
    """User login schema."""
    password: str


class UserResponse(UserBase):
    """User response schema."""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

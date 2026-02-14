"""User schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schemas.auth import UserResponse


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

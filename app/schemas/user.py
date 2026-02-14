"""User schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schemas.auth import UserResponse


class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = Field(None, examples=["new.email@xether.ai"])
    role: Optional[str] = Field(None, examples=["admin"])
    is_active: Optional[bool] = Field(None, examples=[True])
    is_superuser: Optional[bool] = Field(None, examples=[False])


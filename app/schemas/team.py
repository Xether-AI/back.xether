"""Team schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    """Base Team schema."""
    name: str = Field(..., min_length=1, max_length=100, examples=["Research Team"])
    description: Optional[str] = Field(None, max_length=255, examples=["Core research and development team."])



class TeamCreate(TeamBase):
    """Team creation schema."""
    pass


class TeamUpdate(BaseModel):
    """Team update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Updated Research Team"])
    description: Optional[str] = Field(None, max_length=255, examples=["New team description."])



class TeamMember(BaseModel):
    """Team member schema."""
    user_id: int
    role: str

    model_config = {"from_attributes": True}


class TeamMemberAdd(BaseModel):
    """Schema for adding a member to a team."""
    user_id: int = Field(..., examples=[2])
    role: str = Field("viewer", examples=["developer"])



class TeamResponse(TeamBase):
    """Team response schema."""
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

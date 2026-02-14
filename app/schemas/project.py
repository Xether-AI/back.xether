"""Project schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base Project schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    team_id: int


class ProjectCreate(ProjectBase):
    """Project creation schema."""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

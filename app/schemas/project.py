"""Project schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base Project schema."""
    name: str = Field(..., min_length=1, max_length=100, examples=["Image Classification Project"])
    description: Optional[str] = Field(None, max_length=255, examples=["Project for training ResNet models on satellite imagery."])
    team_id: int = Field(..., examples=[1])



class ProjectCreate(ProjectBase):
    """Project creation schema."""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Updated Project Name"])
    description: Optional[str] = Field(None, max_length=255, examples=["Updated description."])



class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

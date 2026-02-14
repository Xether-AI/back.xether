"""Pipeline schemas."""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class PipelineBase(BaseModel):
    """Base Pipeline schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    project_id: int
    config: dict = Field(default_factory=dict)
    is_active: bool = True


class PipelineCreate(PipelineBase):
    """Pipeline creation schema."""
    pass


class PipelineUpdate(BaseModel):
    """Pipeline update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class PipelineResponse(PipelineBase):
    """Pipeline response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PipelineExecutionBase(BaseModel):
    """Base Pipeline Execution schema."""
    pipeline_id: int
    status: str = "pending"
    meta_data: Optional[dict] = None


class PipelineExecutionResponse(PipelineExecutionBase):
    """Pipeline Execution response schema."""
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}

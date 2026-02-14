"""Pipeline schemas."""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class PipelineBase(BaseModel):
    """Base Pipeline schema."""
    name: str = Field(..., min_length=1, max_length=100, examples=["YOLOv8-Training-Pipeline"])
    description: Optional[str] = Field(None, max_length=255, examples=["Pipeline for training YOLOv8 models."])
    project_id: int = Field(..., examples=[1])
    config: dict = Field(default_factory=dict, examples=[{"epochs": 100, "batch_size": 16}])
    is_active: bool = Field(True, examples=[True])



class PipelineCreate(PipelineBase):
    """Pipeline creation schema."""
    pass


class PipelineUpdate(BaseModel):
    """Pipeline update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Updated Pipeline Name"])
    description: Optional[str] = Field(None, max_length=255, examples=["Updated description."])
    config: Optional[dict] = Field(None, examples=[{"epochs": 200}])
    is_active: Optional[bool] = Field(None, examples=[False])



class PipelineResponse(PipelineBase):
    """Pipeline response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PipelineExecutionBase(BaseModel):
    """Base Pipeline Execution schema."""
    pipeline_id: int = Field(..., examples=[1])
    status: str = Field("pending", examples=["running"])
    meta_data: Optional[dict] = Field(None, examples=[{"worker_id": "worker-77"}])



class PipelineExecutionResponse(PipelineExecutionBase):
    """Pipeline Execution response schema."""
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}

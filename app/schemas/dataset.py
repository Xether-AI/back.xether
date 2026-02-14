"""Dataset schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DatasetBase(BaseModel):
    """Base Dataset schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    project_id: int
    storage_path: str = Field(..., min_length=1, max_length=1024)
    meta_data: Optional[dict] = None


class DatasetCreate(DatasetBase):
    """Dataset registration schema."""
    pass


class DatasetUpdate(BaseModel):
    """Dataset update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    meta_data: Optional[dict] = None


class DatasetResponse(DatasetBase):
    """Dataset response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatasetVersionBase(BaseModel):
    """Base Dataset Version schema."""
    version: str = Field(..., min_length=1, max_length=50)
    meta_data: Optional[dict] = None
    storage_path: str = Field(..., min_length=1, max_length=1024)


class DatasetVersionCreate(DatasetVersionBase):
    """Dataset version creation schema."""
    pass


class DatasetVersionResponse(DatasetVersionBase):
    """Dataset version response schema."""
    id: int
    dataset_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

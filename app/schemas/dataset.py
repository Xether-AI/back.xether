"""Dataset schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DatasetBase(BaseModel):
    """Base Dataset schema."""
    name: str = Field(..., min_length=1, max_length=100, examples=["COCO-2017-val"])
    description: Optional[str] = Field(None, max_length=255, examples=["Validation split of the COCO 2017 dataset."])
    project_id: int = Field(..., examples=[1])
    storage_path: str = Field(..., min_length=1, max_length=1024, examples=["s3://xether-datasets/coco/val/"])
    meta_data: Optional[dict] = Field(None, examples=[{"format": "jpg", "size_gb": 1.2}])



class DatasetCreate(DatasetBase):
    """Dataset registration schema."""
    pass


class DatasetUpdate(BaseModel):
    """Dataset update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Updated Dataset Title"])
    description: Optional[str] = Field(None, max_length=255, examples=["Updated description."])
    meta_data: Optional[dict] = Field(None, examples=[{"tags": ["vision", "curated"]}])



class DatasetResponse(DatasetBase):
    """Dataset response schema."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatasetVersionBase(BaseModel):
    """Base Dataset Version schema."""
    version: str = Field(..., min_length=1, max_length=50, examples=["v1.2.0"])
    meta_data: Optional[dict] = Field(None, examples=[{"checksum": "sha256:..."}])
    storage_path: str = Field(..., min_length=1, max_length=1024, examples=["s3://xether-datasets/coco/val/v1.2.0/"])



class DatasetVersionCreate(DatasetVersionBase):
    """Dataset version creation schema."""
    pass


class DatasetVersionResponse(DatasetVersionBase):
    """Dataset version response schema."""
    id: int
    dataset_id: int
    created_at: datetime

    model_config = {"from_attributes": True}

"""Audit schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogBase(BaseModel):
    """Base Audit Log schema."""
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    """Audit Log response schema."""
    id: int
    user_id: Optional[int] = None
    timestamp: datetime

    model_config = {"from_attributes": True}

"""Audit service logic."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import AuditLog


async def create_audit_log(
    db: AsyncSession,
    *,
    user_id: Optional[int] = None,
    action: str,
    resource_type: str,
    resource_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """Create a new audit log entry."""
    db_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


async def list_audit_logs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
) -> List[AuditLog]:
    """List audit logs with filters."""
    query = select(AuditLog)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if resource_id:
        query = query.where(AuditLog.resource_id == resource_id)
        
    query = query.offset(skip).limit(limit).order_by(AuditLog.timestamp.desc())
    result = await db.execute(query)
    return list(result.scalars().all())

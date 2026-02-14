"""Unit tests for Audit Service with mocking."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services import audit as audit_service
from app.models.base import AuditLog

@pytest.mark.asyncio
async def test_create_audit_log_unit():
    """Test creating an audit log entry."""
    mock_db = AsyncMock()
    mock_db.add = MagicMock()
    
    log = await audit_service.create_audit_log(
        mock_db, user_id=1, action="test_action", resource_type="test_res"
    )
    
    assert log.action == "test_action"
    assert log.user_id == 1
    assert mock_db.add.called
    assert mock_db.commit.called

@pytest.mark.asyncio
async def test_list_audit_logs_unit():
    """Test listing audit logs with filters."""
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [AuditLog(id=1, action="A1")]
    mock_db.execute.return_value = mock_result
    
    logs = await audit_service.list_audit_logs(mock_db, user_id=1)
    
    assert len(logs) == 1
    assert logs[0].action == "A1"
    # Verify filter was applied in the generated query if possible, 
    # but here we just verify the call.
    assert mock_db.execute.called

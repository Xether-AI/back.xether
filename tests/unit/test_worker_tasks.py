"""Unit tests for Celery Worker tasks."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.worker.tasks import process_audit_log

@pytest.mark.asyncio
async def test_process_audit_log_task():
    """Test background audit log processing."""
    mock_db = AsyncMock()
    mock_db.__aenter__.return_value = mock_db
    
    # We need to mock the session factory
    with patch("app.worker.tasks.AsyncSessionLocal", return_value=mock_db), \
         patch("app.worker.tasks.audit_service.create_audit_log", new_callable=AsyncMock) as mock_create:
        
        # Call the task synchronously for testing
        process_audit_log(user_id=1, action="test", resource_type="project")
        
        # Since it runs in an event loop (run_until_complete or create_task), 
        # we might need to wait or just verify the call.
        # In this environment, run_until_complete is likely called.
        assert mock_create.called
        args, kwargs = mock_create.call_args
        assert kwargs["user_id"] == 1
        assert kwargs["action"] == "test"

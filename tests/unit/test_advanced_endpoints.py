"""Unit tests for advanced features endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from app.api.v1.endpoints.artifacts import (
    set_retention_policy,
    get_retention_policy,
    get_storage_classes,
    SetRetentionPolicyRequest,
    RetentionPolicyResponse,
    StorageClassInfo
)


@pytest.mark.asyncio
async def test_set_retention_policy_endpoint_success():
    """Test successful retention policy setting endpoint."""
    mock_client = AsyncMock()
    mock_client.set_retention_policy.return_value = {
        "status": "set",
        "project_id": "test-project",
        "max_bytes": 1000000000,
        "ttl_days": 30
    }
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        request = SetRetentionPolicyRequest(
            project_id="test-project",
            max_bytes=1000000000,
            ttl_days=30
        )
        
        result = await set_retention_policy("test-project", request, mock_client, mock_client)
        
        assert result["status"] == "set"
        assert result["project_id"] == "test-project"
        assert result["max_bytes"] == 1000000000
        assert result["ttl_days"] == 30
        mock_client.set_retention_policy.assert_called_once_with("test-project", 1000000000, 30)


@pytest.mark.asyncio
async def test_get_storage_classes_endpoint_success():
    """Test successful storage classes endpoint."""
    mock_client = AsyncMock()
    mock_client.get_storage_classes.return_value = {
        "storage_classes": ["standard", "premium", "archive"]
    }
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        result = await get_storage_classes(mock_client, mock_client)
        
        assert result["storage_classes"] == ["standard", "premium", "archive"]
        mock_client.get_storage_classes.assert_called_once()


@pytest.mark.asyncio
async def test_advanced_features_endpoint_error_handling():
    """Test advanced features endpoint error handling."""
    mock_client = AsyncMock()
    mock_client.set_retention_policy.side_effect = Exception("Storage error")
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        request = SetRetentionPolicyRequest(
            project_id="test-project",
            max_bytes=1000000000,
            ttl_days=30
        )
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await set_retention_policy("test-project", request, mock_client, mock_client)


# Test request/response models
def test_set_retention_policy_request_model():
    """Test SetRetentionPolicyRequest model validation."""
    request = SetRetentionPolicyRequest(
        project_id="test-project",
        max_bytes=1000000000,
        ttl_days=30
    )
    assert request.project_id == "test-project"
    assert request.max_bytes == 1000000000
    assert request.ttl_days == 30


def test_storage_class_info_model():
    """Test StorageClassInfo model validation."""
    storage_class = StorageClassInfo(
        name="standard",
        description="Standard storage class",
        cost_per_gb=0.023
    )
    assert storage_class.name == "standard"
    assert storage_class.description == "Standard storage class"
    assert storage_class.cost_per_gb == 0.023

"""Unit tests for advanced features."""

import pytest
from unittest.mock import AsyncMock, patch
from app.grpc.clients.artifact_storage_client import ArtifactStorageClient


@pytest.mark.asyncio
async def test_set_retention_policy_success():
    """Test successful retention policy setting."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = "set"
        mock_response.project_id = "test-project"
        mock_response.max_bytes = 1000000000
        mock_response.ttl_days = 30
        mock_response.HasField.return_value = True
        mock_stub.return_value.SetRetentionPolicy.return_value = mock_response
        
        await client.connect()
        result = await client.set_retention_policy("test-project", 1000000000, 30)
        
        assert result["status"] == "set"
        assert result["project_id"] == "test-project"
        assert result["max_bytes"] == 1000000000
        assert result["ttl_days"] == 30


@pytest.mark.asyncio
async def test_get_storage_classes_success():
    """Test successful storage classes retrieval."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.storage_classes = ["standard", "premium", "archive"]
        mock_stub.return_value.GetStorageClasses.return_value = mock_response
        
        await client.connect()
        result = await client.get_storage_classes()
        
        assert result["storage_classes"] == ["standard", "premium", "archive"]


@pytest.mark.asyncio
async def test_advanced_features_error_handling():
    """Test advanced features error handling."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.set_retention_policy("test-project", 1000000000, 30)
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.get_storage_classes()

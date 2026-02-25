"""Unit tests for Artifact Storage gRPC client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.grpc.clients.artifact_storage_client import ArtifactStorageClient


@pytest.mark.asyncio
async def test_delete_artifact_success():
    """Test successful artifact deletion."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = "deleted"
        mock_stub.return_value.DeleteArtifact.return_value = mock_response
        
        await client.connect()
        result = await client.delete_artifact("test-artifact-id")
        
        assert result is True


@pytest.mark.asyncio
async def test_delete_artifact_failure():
    """Test artifact deletion failure."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status = "error"
        mock_stub.return_value.DeleteArtifact.return_value = mock_response
        
        await client.connect()
        result = await client.delete_artifact("test-artifact-id")
        
        assert result is False


@pytest.mark.asyncio
async def test_validate_checksum_success():
    """Test successful checksum validation."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub, \
         patch("app.grpc.clients.artifact_storage_client.datetime") as mock_datetime:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.valid = True
        mock_response.expected_checksum = "abc123"
        mock_response.actual_checksum = "abc123"
        mock_response.HasField.return_value = True
        mock_response.validation_time.ToDatetime.return_value.isoformat.return_value = "2026-02-25T15:00:00"
        mock_stub.return_value.ValidateChecksum.return_value = mock_response
        
        await client.connect()
        result = await client.validate_checksum("test-artifact-id")
        
        assert result["valid"] is True
        assert result["expected_checksum"] == "abc123"
        assert result["actual_checksum"] == "abc123"
        assert result["validation_time"] == "2026-02-25T15:00:00"


@pytest.mark.asyncio
async def test_validate_checksum_failure():
    """Test checksum validation failure."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock failed response
        mock_response = MagicMock()
        mock_response.valid = False
        mock_response.expected_checksum = "abc123"
        mock_response.HasField.return_value = False
        mock_stub.return_value.ValidateChecksum.return_value = mock_response
        
        await client.connect()
        result = await client.validate_checksum("test-artifact-id")
        
        assert result["valid"] is False
        assert result["expected_checksum"] == "abc123"
        assert result["actual_checksum"] is None


@pytest.mark.asyncio
async def test_client_not_connected_error():
    """Test error when client is not connected."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.delete_artifact("test-id")
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.validate_checksum("test-id")

"""Unit tests for artifact version management."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.grpc.clients.artifact_storage_client import ArtifactStorageClient


@pytest.mark.asyncio
async def test_get_versions_success():
    """Test successful artifact version retrieval."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_version = MagicMock()
        mock_version.version_id = "version-123"
        mock_version.size = 1024
        mock_version.checksum_sha256 = "abc123"
        mock_version.created_at.ToDatetime.return_value.isoformat.return_value = "2026-02-25T16:00:00"
        mock_version.is_latest = True
        mock_version.HasField.return_value = True
        
        mock_response.versions = [mock_version]
        mock_stub.return_value.GetVersions.return_value = mock_response
        
        await client.connect()
        result = await client.get_versions("test-artifact-id")
        
        assert len(result) == 1
        assert result[0]["version_id"] == "version-123"
        assert result[0]["size"] == 1024
        assert result[0]["checksum_sha256"] == "abc123"
        assert result[0]["is_latest"] is True


@pytest.mark.asyncio
async def test_restore_artifact_success():
    """Test successful artifact restoration."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = "restored"
        mock_response.restored_version_id = "version-123"
        mock_response.HasField.return_value = True
        mock_response.restoration_time.ToDatetime.return_value.isoformat.return_value = "2026-02-25T16:00:00"
        mock_stub.return_value.RestoreArtifact.return_value = mock_response
        
        await client.connect()
        result = await client.restore_artifact("test-artifact-id", "version-123")
        
        assert result["status"] == "restored"
        assert result["restored_version_id"] == "version-123"
        assert result["restoration_time"] == "2026-02-25T16:00:00"


@pytest.mark.asyncio
async def test_restore_artifact_latest():
    """Test artifact restoration to latest version."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status = "restored"
        mock_response.HasField.return_value = False  # No version_id specified
        mock_stub.return_value.RestoreArtifact.return_value = mock_response
        
        await client.connect()
        result = await client.restore_artifact("test-artifact-id", None)
        
        assert result["status"] == "restored"
        assert result["restored_version_id"] is None


@pytest.mark.asyncio
async def test_version_management_error_handling():
    """Test version management error handling."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.get_versions("test-id")
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.restore_artifact("test-id", "version-123")

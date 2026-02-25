"""Unit tests for multipart upload functionality."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.grpc.clients.artifact_storage_client import ArtifactStorageClient


@pytest.mark.asyncio
async def test_initiate_multipart_upload_success():
    """Test successful multipart upload initiation."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.artifact_id = "test-artifact-id"
        mock_response.upload_id = "test-upload-id"
        mock_stub.return_value.InitiateMultipart.return_value = mock_response
        
        await client.connect()
        result = await client.initiate_multipart_upload(
            name="large-file.zip",
            bucket="test-bucket",
            key="test-key",
            content_type="application/zip",
            pipeline_id="pipeline-1"
        )
        
        assert result["artifact_id"] == "test-artifact-id"
        assert result["upload_id"] == "test-upload-id"


@pytest.mark.asyncio
async def test_get_multipart_part_url_success():
    """Test successful multipart part URL generation."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.part_url = "https://example.com/upload-part"
        mock_response.HasField.return_value = True
        mock_response.expires_at.ToDatetime.return_value.isoformat.return_value = "2026-02-25T16:00:00"
        mock_stub.return_value.GetMultipartPartURL.return_value = mock_response
        
        await client.connect()
        result = await client.get_multipart_part_url(
            artifact_id="test-artifact-id",
            upload_id="test-upload-id",
            part_number=1
        )
        
        assert result["part_url"] == "https://example.com/upload-part"
        assert result["expires_at"] == "2026-02-25T16:00:00"


@pytest.mark.asyncio
async def test_complete_multipart_upload_success():
    """Test successful multipart upload completion."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with patch("app.grpc.clients.artifact_storage_client.grpc.aio.insecure_channel"), \
         patch("app.grpc.generated.artifact_pb2_grpc.ArtifactServiceStub") as mock_stub:
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.version_id = "test-version-id"
        mock_response.HasField.return_value = True
        mock_stub.return_value.CompleteMultipart.return_value = mock_response
        
        await client.connect()
        result = await client.complete_multipart_upload(
            artifact_id="test-artifact-id",
            upload_id="test-upload-id",
            parts=[
                {"part_number": 1, "etag": "etag1"},
                {"part_number": 2, "etag": "etag2"}
            ]
        )
        
        assert result["status"] == "completed"
        assert result["version_id"] == "test-version-id"


@pytest.mark.asyncio
async def test_multipart_upload_error_handling():
    """Test multipart upload error handling."""
    client = ArtifactStorageClient("localhost", 50051, "test-key")
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.initiate_multipart_upload("test", "bucket", "key")
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.get_multipart_part_url("test-id", "upload-id", 1)
    
    with pytest.raises(RuntimeError, match="Client not connected"):
        await client.complete_multipart_upload("test-id", "upload-id", [])

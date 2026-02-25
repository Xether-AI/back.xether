"""Unit tests for multipart upload endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from app.api.v1.endpoints.artifacts import (
    initiate_multipart_upload,
    get_multipart_part_url,
    complete_multipart_upload,
    InitiateMultipartRequest,
    InitiateMultipartResponse,
    MultipartPartURLRequest,
    MultipartPartURLResponse,
    CompletePart,
    CompleteMultipartRequest,
    CompleteMultipartResponse
)


@pytest.mark.asyncio
async def test_initiate_multipart_endpoint_success():
    """Test successful multipart upload initiation endpoint."""
    mock_client = AsyncMock()
    mock_client.initiate_multipart_upload.return_value = {
        "artifact_id": "test-artifact-id",
        "upload_id": "test-upload-id"
    }
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        request = InitiateMultipartRequest(
            name="large-file.zip",
            bucket="test-bucket",
            key="test-key",
            content_type="application/zip"
        )
        
        result = await initiate_multipart_upload(request, mock_client, mock_client)
        
        assert result["artifact_id"] == "test-artifact-id"
        assert result["upload_id"] == "test-upload-id"
        mock_client.initiate_multipart_upload.assert_called_once()


@pytest.mark.asyncio
async def test_get_multipart_part_url_endpoint_success():
    """Test successful multipart part URL endpoint."""
    mock_client = AsyncMock()
    mock_client.get_multipart_part_url.return_value = {
        "part_url": "https://example.com/upload-part",
        "expires_at": "2026-02-25T16:00:00"
    }
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        request = MultipartPartURLRequest(
            artifact_id="test-artifact-id",
            upload_id="test-upload-id",
            part_number=1
        )
        
        result = await get_multipart_part_url(request, mock_client, mock_client)
        
        assert result["part_url"] == "https://example.com/upload-part"
        assert result["expires_at"] == "2026-02-25T16:00:00"
        mock_client.get_multipart_part_url.assert_called_once()


@pytest.mark.asyncio
async def test_complete_multipart_endpoint_success():
    """Test successful multipart upload completion endpoint."""
    mock_client = AsyncMock()
    mock_client.complete_multipart_upload.return_value = {
        "status": "completed",
        "version_id": "test-version-id"
    }
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        parts = [
            CompletePart(part_number=1, etag="etag1"),
            CompletePart(part_number=2, etag="etag2")
        ]
        request = CompleteMultipartRequest(
            artifact_id="test-artifact-id",
            upload_id="test-upload-id",
            parts=parts
        )
        
        result = await complete_multipart_upload(request, mock_client, mock_client)
        
        assert result["status"] == "completed"
        assert result["version_id"] == "test-version-id"
        mock_client.complete_multipart_upload.assert_called_once()


@pytest.mark.asyncio
async def test_multipart_endpoint_error_handling():
    """Test multipart upload endpoint error handling."""
    mock_client = AsyncMock()
    mock_client.initiate_multipart_upload.side_effect = Exception("Storage error")
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        request = InitiateMultipartRequest(
            name="test.txt",
            bucket="test-bucket",
            key="test-key"
        )
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await initiate_multipart_upload(request, mock_client, mock_client)


# Test request/response models
def test_initiate_multipart_request_model():
    """Test InitiateMultipartRequest model validation."""
    request = InitiateMultipartRequest(
        name="large-file.zip",
        bucket="test-bucket",
        key="test-key",
        content_type="application/zip",
        pipeline_id="pipeline-1",
        retention_days=30
    )
    assert request.name == "large-file.zip"
    assert request.bucket == "test-bucket"
    assert request.content_type == "application/zip"
    assert request.pipeline_id == "pipeline-1"
    assert request.retention_days == 30


def test_complete_part_model():
    """Test CompletePart model validation."""
    part = CompletePart(part_number=1, etag="test-etag")
    assert part.part_number == 1
    assert part.etag == "test-etag"


def test_complete_multipart_request_model():
    """Test CompleteMultipartRequest model validation."""
    parts = [
        CompletePart(part_number=1, etag="etag1"),
        CompletePart(part_number=2, etag="etag2")
    ]
    request = CompleteMultipartRequest(
        artifact_id="test-id",
        upload_id="upload-id",
        parts=parts
    )
    assert request.artifact_id == "test-id"
    assert request.upload_id == "upload-id"
    assert len(request.parts) == 2
    assert request.parts[0].part_number == 1
    assert request.parts[0].etag == "etag1"

"""Unit tests for artifact endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.endpoints.artifacts import (
    delete_artifact, 
    validate_checksum,
    UploadURLRequest,
    UploadURLResponse,
    ArtifactMetadata
)

client = TestClient(app)


@pytest.mark.asyncio
async def test_delete_artifact_success():
    """Test successful artifact deletion."""
    mock_client = AsyncMock()
    mock_client.delete_artifact.return_value = True
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        result = await delete_artifact("test-artifact-id", mock_client, mock_client)
        
        assert result["status"] == "deleted"
        assert result["artifact_id"] == "test-artifact-id"
        mock_client.delete_artifact.assert_called_once_with("test-artifact-id")


@pytest.mark.asyncio
async def test_delete_artifact_failure():
    """Test artifact deletion failure."""
    mock_client = AsyncMock()
    mock_client.delete_artifact.return_value = False
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await delete_artifact("test-artifact-id", mock_client, mock_client)


@pytest.mark.asyncio
async def test_validate_checksum_success():
    """Test successful checksum validation."""
    mock_client = AsyncMock()
    mock_client.validate_checksum.return_value = {
        "valid": True,
        "expected_checksum": "abc123",
        "actual_checksum": "abc123",
        "validation_time": "2026-02-25T15:00:00"
    }
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        result = await validate_checksum("test-artifact-id", mock_client, mock_client)
        
        assert result["valid"] is True
        assert result["expected_checksum"] == "abc123"
        assert result["actual_checksum"] == "abc123"
        mock_client.validate_checksum.assert_called_once_with("test-artifact-id")


@pytest.mark.asyncio
async def test_validate_checksum_failure():
    """Test checksum validation failure."""
    mock_client = AsyncMock()
    mock_client.validate_checksum.side_effect = Exception("Storage error")
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await validate_checksum("test-artifact-id", mock_client, mock_client)


# Test the request/response models
def test_upload_url_request_model():
    """Test UploadURLRequest model validation."""
    # Valid request
    request = UploadURLRequest(
        name="test.txt",
        bucket="test-bucket",
        key="test-key",
        content_type="text/plain"
    )
    assert request.name == "test.txt"
    assert request.bucket == "test-bucket"
    assert request.key == "test-key"
    assert request.content_type == "text/plain"


def test_upload_url_response_model():
    """Test UploadURLResponse model validation."""
    response = UploadURLResponse(
        artifact_id="test-id",
        upload_url="https://example.com/upload"
    )
    assert response.artifact_id == "test-id"
    assert response.upload_url == "https://example.com/upload"


def test_artifact_metadata_model():
    """Test ArtifactMetadata model validation."""
    metadata = ArtifactMetadata(
        id="test-id",
        name="test.txt",
        bucket="test-bucket",
        key="test-key",
        size=1024,
        content_type="text/plain",
        checksum_sha256="abc123",
        pipeline_id="pipeline-1",
        project_id="project-1"
    )
    assert metadata.id == "test-id"
    assert metadata.name == "test.txt"
    assert metadata.size == 1024
    assert metadata.checksum_sha256 == "abc123"
    assert metadata.pipeline_id == "pipeline-1"
    assert metadata.project_id == "project-1"

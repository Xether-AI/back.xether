"""Unit tests for artifact version management endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from app.api.v1.endpoints.artifacts import (
    get_artifact_versions,
    restore_artifact,
    ArtifactVersion,
    RestoreArtifactRequest,
    RestoreArtifactResponse
)


@pytest.mark.asyncio
async def test_get_artifact_versions_endpoint_success():
    """Test successful artifact versions endpoint."""
    mock_client = AsyncMock()
    mock_client.get_versions.return_value = [
        {
            "version_id": "version-123",
            "size": 1024,
            "checksum_sha256": "abc123",
            "created_at": "2026-02-25T16:00:00",
            "is_latest": True
        }
    ]
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        result = await get_artifact_versions("test-artifact-id", mock_client, mock_client)
        
        assert len(result) == 1
        assert result[0]["version_id"] == "version-123"
        assert result[0]["is_latest"] is True
        mock_client.get_versions.assert_called_once_with("test-artifact-id")


@pytest.mark.asyncio
async def test_restore_artifact_endpoint_success():
    """Test successful artifact restoration endpoint."""
    mock_client = AsyncMock()
    mock_client.restore_artifact.return_value = {
        "status": "restored",
        "restored_version_id": "version-123",
        "restoration_time": "2026-02-25T16:00:00"
    }
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        request = RestoreArtifactRequest(version_id="version-123")
        result = await restore_artifact("test-artifact-id", request, mock_client, mock_client)
        
        assert result["status"] == "restored"
        assert result["restored_version_id"] == "version-123"
        mock_client.restore_artifact.assert_called_once_with("test-artifact-id", "version-123")


@pytest.mark.asyncio
async def test_restore_artifact_endpoint_latest():
    """Test artifact restoration to latest version."""
    mock_client = AsyncMock()
    mock_client.restore_artifact.return_value = {
        "status": "restored",
        "restored_version_id": None,
        "restoration_time": "2026-02-25T16:00:00"
    }
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        request = RestoreArtifactRequest()  # No version_id specified
        result = await restore_artifact("test-artifact-id", request, mock_client, mock_client)
        
        assert result["status"] == "restored"
        assert result["restored_version_id"] is None
        mock_client.restore_artifact.assert_called_once_with("test-artifact-id", None)


@pytest.mark.asyncio
async def test_version_management_endpoint_error_handling():
    """Test version management endpoint error handling."""
    mock_client = AsyncMock()
    mock_client.get_versions.side_effect = Exception("Storage error")
    
    with patch("app.api.v1.endpoints.artifacts.get_artifact_storage_client", return_value=mock_client), \
         patch("app.api.v1.endpoints.artifacts.deps.get_current_user", return_value={"id": 1}):
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await get_artifact_versions("test-artifact-id", mock_client, mock_client)


# Test request/response models
def test_artifact_version_model():
    """Test ArtifactVersion model validation."""
    version = ArtifactVersion(
        version_id="version-123",
        size=1024,
        checksum_sha256="abc123",
        created_at="2026-02-25T16:00:00",
        is_latest=True
    )
    assert version.version_id == "version-123"
    assert version.size == 1024
    assert version.checksum_sha256 == "abc123"
    assert version.is_latest is True


def test_restore_artifact_request_model():
    """Test RestoreArtifactRequest model validation."""
    request = RestoreArtifactRequest(version_id="version-123")
    assert request.version_id == "version-123"


def test_restore_artifact_response_model():
    """Test RestoreArtifactResponse model validation."""
    response = RestoreArtifactResponse(
        status="restored",
        restored_version_id="version-123",
        restoration_time="2026-02-25T16:00:00"
    )
    assert response.status == "restored"
    assert response.restored_version_id == "version-123"
    assert response.restoration_time == "2026-02-25T16:00:00"

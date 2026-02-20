"""Artifact management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from app.core.grpc_clients import get_artifact_storage_client
from app.grpc.clients.artifact_storage_client import ArtifactStorageClient
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


# Request/Response Models
class UploadURLRequest(BaseModel):
    """Request for pre-signed upload URL."""
    name: str = Field(..., description="Artifact name")
    bucket: str = Field(..., description="S3 bucket name")
    key: str = Field(..., description="S3 object key")
    content_type: str = Field(..., description="MIME type")
    expires_in_seconds: int = Field(default=3600, description="URL expiration (seconds)")
    pipeline_id: Optional[str] = Field(None, description="Associated pipeline ID")
    execution_id: Optional[str] = Field(None, description="Associated execution ID")
    project_id: Optional[str] = Field(None, description="Associated project ID")


class UploadURLResponse(BaseModel):
    """Response with pre-signed upload URL."""
    artifact_id: str = Field(..., description="Unique artifact ID")
    upload_url: str = Field(..., description="Pre-signed S3 upload URL")


class CompleteUploadRequest(BaseModel):
    """Request to mark upload as complete."""
    size: int = Field(..., description="File size in bytes")
    checksum: str = Field(..., description="SHA-256 checksum")
    version_id: Optional[str] = Field(None, description="S3 version ID")


class DownloadURLResponse(BaseModel):
    """Response with pre-signed download URL."""
    download_url: str = Field(..., description="Pre-signed S3 download URL")


class ArtifactMetadata(BaseModel):
    """Artifact metadata."""
    id: str
    name: str
    bucket: str
    key: str
    size: int
    content_type: str
    checksum_sha256: str
    version_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    execution_id: Optional[str] = None
    project_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Endpoints
@router.post("/upload", response_model=UploadURLResponse, status_code=200)
async def request_upload_url(
    request: UploadURLRequest,
    current_user: User = Depends(get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Request a pre-signed URL for uploading an artifact.
    
    The client should:
    1. Call this endpoint to get upload URL
    2. Upload file directly to S3 using the URL
    3. Call complete_upload endpoint with file details
    """
    try:
        result = await client.get_upload_url(
            name=request.name,
            bucket=request.bucket,
            key=request.key,
            content_type=request.content_type,
            expires_in_seconds=request.expires_in_seconds,
            pipeline_id=request.pipeline_id,
            execution_id=request.execution_id,
            project_id=request.project_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate upload URL: {str(e)}"
        )


@router.post("/{artifact_id}/complete", status_code=200)
async def complete_upload(
    artifact_id: str,
    request: CompleteUploadRequest,
    current_user: User = Depends(get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Mark an artifact upload as complete.
    
    Call this after successfully uploading the file to S3.
    """
    try:
        success = await client.complete_upload(
            artifact_id=artifact_id,
            size=request.size,
            checksum=request.checksum,
            version_id=request.version_id or ""
        )
        
        if success:
            return {"status": "completed", "artifact_id": artifact_id}
        else:
            raise HTTPException(status_code=500, detail="Upload completion failed")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete upload: {str(e)}"
        )


@router.get("/{artifact_id}/download", response_model=DownloadURLResponse)
async def get_download_url(
    artifact_id: str,
    expires_in_seconds: int = Query(default=3600, description="URL expiration (seconds)"),
    current_user: User = Depends(get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Get a pre-signed URL for downloading an artifact.
    
    The URL is valid for the specified duration (default: 1 hour).
    """
    try:
        url = await client.get_download_url(
            artifact_id=artifact_id,
            expires_in_seconds=expires_in_seconds
        )
        return {"download_url": url}
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Artifact not found or download URL generation failed: {str(e)}"
        )


@router.get("/{artifact_id}", response_model=ArtifactMetadata)
async def get_artifact_metadata(
    artifact_id: str,
    current_user: User = Depends(get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Retrieve metadata for a specific artifact.
    """
    try:
        metadata = await client.get_metadata(artifact_id)
        return metadata
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Artifact not found: {str(e)}"
        )


@router.get("/", response_model=list[ArtifactMetadata])
async def list_artifacts(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    pipeline_id: Optional[str] = Query(None, description="Filter by pipeline ID"),
    current_user: User = Depends(get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    List artifacts with optional filters.
    """
    try:
        artifacts = await client.list_artifacts(
            project_id=project_id,
            pipeline_id=pipeline_id
        )
        return artifacts
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list artifacts: {str(e)}"
        )

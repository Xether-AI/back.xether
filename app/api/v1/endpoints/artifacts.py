"""Artifact management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List

from app.core.grpc_clients import get_artifact_storage_client
from app.grpc.clients.artifact_storage_client import ArtifactStorageClient
from app.api import deps
from app.models.base import User

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
    current_user: User = Depends(deps.get_current_user),
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
    current_user: User = Depends(deps.get_current_user),
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
    current_user: User = Depends(deps.get_current_user),
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
    current_user: User = Depends(deps.get_current_user),
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
    include_versions: bool = Query(False, description="Include version information"),
    current_user: User = Depends(deps.get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    List artifacts with optional filters and version information.
    """
    try:
        artifacts = await client.list_artifacts(
            project_id=project_id,
            pipeline_id=pipeline_id
        )
        
        # If version information requested, fetch versions for each artifact
        if include_versions:
            for artifact in artifacts:
                try:
                    artifact["versions"] = await client.get_versions(artifact["id"])
                except Exception:
                    # If we can't get versions, don't fail the entire request
                    artifact["versions"] = []
        
        return artifacts
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list artifacts: {str(e)}"
        )


@router.delete("/{artifact_id}", status_code=status.HTTP_200_OK)
async def delete_artifact(
    artifact_id: str,
    current_user: User = Depends(deps.get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Delete an artifact.
    """
    try:
        success = await client.delete_artifact(artifact_id)
        if success:
            return {"status": "deleted", "artifact_id": artifact_id}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete artifact"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete artifact: {str(e)}"
        )


@router.post("/{artifact_id}/validate-checksum", response_model=dict)
async def validate_checksum(
    artifact_id: str,
    current_user: User = Depends(deps.get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Validate artifact checksum integrity.
    """
    try:
        validation_result = await client.validate_checksum(artifact_id)
        return validation_result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate checksum: {str(e)}"
        )


# Multipart Upload Request/Response Models
class InitiateMultipartRequest(BaseModel):
    """Request to initiate multipart upload."""
    name: str = Field(..., description="Artifact name")
    bucket: str = Field(..., description="S3 bucket name")
    key: str = Field(..., description="S3 object key")
    content_type: str = Field(default="application/octet-stream", description="MIME type")
    pipeline_id: Optional[str] = Field(None, description="Associated pipeline ID")
    execution_id: Optional[str] = Field(None, description="Associated execution ID")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    retention_days: Optional[int] = Field(None, description="Retention period in days")
    storage_class: Optional[str] = Field(None, description="S3 storage class")


class InitiateMultipartResponse(BaseModel):
    """Response with upload ID and artifact ID."""
    artifact_id: str = Field(..., description="Unique artifact ID")
    upload_id: str = Field(..., description="Multipart upload ID")


class MultipartPartURLRequest(BaseModel):
    """Request for multipart part upload URL."""
    artifact_id: str = Field(..., description="Artifact ID")
    upload_id: str = Field(..., description="Multipart upload ID")
    part_number: int = Field(..., description="Part number", ge=1)
    expires_in: int = Field(default=3600, description="URL expiration (seconds)")


class MultipartPartURLResponse(BaseModel):
    """Response with part upload URL."""
    part_url: str = Field(..., description="Pre-signed URL for part upload")
    expires_at: Optional[str] = Field(None, description="URL expiration time")


class CompletePart(BaseModel):
    """Completed multipart part."""
    part_number: int = Field(..., description="Part number", ge=1)
    etag: str = Field(..., description="Part ETag from S3")


class CompleteMultipartRequest(BaseModel):
    """Request to complete multipart upload."""
    artifact_id: str = Field(..., description="Artifact ID")
    upload_id: str = Field(..., description="Multipart upload ID")
    parts: List[CompletePart] = Field(..., description="List of completed parts")


class CompleteMultipartResponse(BaseModel):
    """Response with completion status."""
    status: str = Field(..., description="Upload completion status")
    version_id: Optional[str] = Field(None, description="S3 object version ID")


# Multipart Upload Endpoints
@router.post("/multipart/initiate", response_model=InitiateMultipartResponse, status_code=status.HTTP_200_OK)
async def initiate_multipart_upload(
    request: InitiateMultipartRequest,
    current_user: User = Depends(deps.get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Initiate multipart upload for large files.
    """
    try:
        result = await client.initiate_multipart_upload(
            name=request.name,
            bucket=request.bucket,
            key=request.key,
            content_type=request.content_type,
            pipeline_id=request.pipeline_id,
            execution_id=request.execution_id,
            project_id=request.project_id,
            retention_days=request.retention_days,
            storage_class=request.storage_class
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate multipart upload: {str(e)}"
        )


@router.post("/multipart/part-url", response_model=MultipartPartURLResponse, status_code=status.HTTP_200_OK)
async def get_multipart_part_url(
    request: MultipartPartURLRequest,
    current_user: User = Depends(deps.get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Get pre-signed URL for uploading a multipart part.
    """
    try:
        result = await client.get_multipart_part_url(
            artifact_id=request.artifact_id,
            upload_id=request.upload_id,
            part_number=request.part_number,
            expires_in=request.expires_in
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get multipart part URL: {str(e)}"
        )


@router.post("/multipart/complete", response_model=CompleteMultipartResponse, status_code=status.HTTP_200_OK)
async def complete_multipart_upload(
    request: CompleteMultipartRequest,
    current_user: User = Depends(deps.get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Complete multipart upload and assemble final object.
    """
    try:
        # Convert Pydantic parts to dict for gRPC client
        parts_dict = [{"part_number": part.part_number, "etag": part.etag} for part in request.parts]
        
        result = await client.complete_multipart_upload(
            artifact_id=request.artifact_id,
            upload_id=request.upload_id,
            parts=parts_dict
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete multipart upload: {str(e)}"
        )


# Version Management Request/Response Models
class ArtifactVersion(BaseModel):
    """Artifact version information."""
    version_id: Optional[str] = Field(None, description="S3 version ID")
    size: int = Field(..., description="Version size in bytes")
    checksum_sha256: Optional[str] = Field(None, description="SHA256 checksum")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    is_latest: bool = Field(False, description="Whether this is the latest version")


class RestoreArtifactRequest(BaseModel):
    """Request to restore an artifact."""
    version_id: Optional[str] = Field(None, description="Target version ID (optional)")


class RestoreArtifactResponse(BaseModel):
    """Response with restoration status."""
    status: str = Field(..., description="Restoration status")
    restored_version_id: Optional[str] = Field(None, description="Restored version ID")
    restoration_time: Optional[str] = Field(None, description="Restoration timestamp")


# Version Management Endpoints
@router.get("/{artifact_id}/versions", response_model=list[ArtifactVersion], status_code=status.HTTP_200_OK)
async def get_artifact_versions(
    artifact_id: str,
    current_user: User = Depends(deps.get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Get version history for an artifact.
    """
    try:
        versions = await client.get_versions(artifact_id)
        return versions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get artifact versions: {str(e)}"
        )


@router.post("/{artifact_id}/restore", response_model=RestoreArtifactResponse, status_code=status.HTTP_200_OK)
async def restore_artifact(
    artifact_id: str,
    request: RestoreArtifactRequest,
    current_user: User = Depends(deps.get_current_user),
    client: ArtifactStorageClient = Depends(get_artifact_storage_client)
):
    """
    Restore an artifact to a specific version.
    """
    try:
        result = await client.restore_artifact(
            artifact_id=artifact_id,
            version_id=request.version_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restore artifact: {str(e)}"
        )

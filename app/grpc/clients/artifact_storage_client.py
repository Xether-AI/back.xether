"""gRPC client for Artifact Storage service."""

import grpc
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ArtifactStorageClient:
    """
    gRPC client for communicating with Artifact Storage service.
    
    Provides methods for:
    - Requesting pre-signed upload URLs
    - Completing uploads
    - Requesting pre-signed download URLs
    - Retrieving artifact metadata
    - Listing artifacts
    """
    
    def __init__(self, host: str, port: int, api_key: str):
        """
        Initialize Artifact Storage gRPC client.
        
        Args:
            host: Artifact Storage service hostname
            port: gRPC port (typically 50051)
            api_key: Admin API Key for authentication
        """
        self.address = f"{host}:{port}"
        self.api_key = api_key
        self.channel: Optional[grpc.aio.Channel] = None
        self.stub = None
        
    async def connect(self):
        """Establish gRPC connection to Artifact Storage service."""
        try:
            # Import generated stubs
            from app.grpc.generated import artifact_pb2_grpc
            
            # Create async channel
            self.channel = grpc.aio.insecure_channel(self.address)
            self.stub = artifact_pb2_grpc.ArtifactServiceStub(self.channel)
            
            logger.info(f"Connected to Artifact Storage gRPC at {self.address}")
        except Exception as e:
            logger.error(f"Failed to connect to Artifact Storage: {e}")
            raise
    
    async def get_upload_url(
        self,
        name: str,
        bucket: str,
        key: str,
        content_type: str,
        expires_in_seconds: int = 3600,
        pipeline_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Request a pre-signed upload URL for artifact storage.
        
        Args:
            name: Artifact name
            bucket: S3 bucket name
            key: S3 object key
            content_type: MIME type
            expires_in_seconds: URL expiration time (default: 1 hour)
            pipeline_id: Optional pipeline ID
            execution_id: Optional execution ID
            project_id: Optional project ID
            
        Returns:
            Dict with artifact_id and upload_url
        """
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            from app.grpc.generated import artifact_pb2
            
            request = artifact_pb2.UploadURLRequest(
                name=name,
                bucket=bucket,
                key=key,
                content_type=content_type,
                expires_in_seconds=expires_in_seconds,
                pipeline_id=pipeline_id or "",
                execution_id=execution_id or "",
                project_id=project_id or ""
            )
            
            metadata = (("x-api-key", self.api_key),)
            response = await self.stub.GetUploadURL(request, metadata=metadata)
            
            return {
                "artifact_id": response.artifact_id,
                "upload_url": response.upload_url
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error getting upload URL: {e.code()} - {e.details()}")
            raise
    
    async def complete_upload(
        self,
        artifact_id: str,
        size: int,
        checksum: str,
        version_id: str = ""
    ) -> bool:
        """
        Mark an artifact upload as complete.
        
        Args:
            artifact_id: Artifact ID from get_upload_url
            size: File size in bytes
            checksum: SHA-256 checksum
            version_id: Optional S3 version ID
            
        Returns:
            True if successful
        """
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            from app.grpc.generated import artifact_pb2
            
            request = artifact_pb2.CompleteUploadRequest(
                artifact_id=artifact_id,
                size=size,
                checksum=checksum,
                version_id=version_id
            )
            
            metadata = (("x-api-key", self.api_key),)
            response = await self.stub.CompleteUpload(request, metadata=metadata)
            
            return response.status == "completed"
        except grpc.RpcError as e:
            logger.error(f"gRPC error completing upload: {e.code()} - {e.details()}")
            raise
    
    async def get_download_url(
        self,
        artifact_id: str,
        expires_in_seconds: int = 3600
    ) -> str:
        """
        Request a pre-signed download URL for an artifact.
        
        Args:
            artifact_id: Artifact ID
            expires_in_seconds: URL expiration time (default: 1 hour)
            
        Returns:
            Pre-signed download URL
        """
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            from app.grpc.generated import artifact_pb2
            
            request = artifact_pb2.DownloadURLRequest(
                artifact_id=artifact_id,
                expires_in_seconds=expires_in_seconds
            )
            
            metadata = (("x-api-key", self.api_key),)
            response = await self.stub.GetDownloadURL(request, metadata=metadata)
            
            return response.download_url
        except grpc.RpcError as e:
            logger.error(f"gRPC error getting download URL: {e.code()} - {e.details()}")
            raise
    
    async def get_metadata(self, artifact_id: str) -> Dict[str, Any]:
        """
        Retrieve artifact metadata.
        
        Args:
            artifact_id: Artifact ID
            
        Returns:
            Dict with artifact metadata
        """
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            from app.grpc.generated import artifact_pb2
            
            request = artifact_pb2.GetMetadataRequest(artifact_id=artifact_id)
            
            metadata = (("x-api-key", self.api_key),)
            response = await self.stub.GetMetadata(request, metadata=metadata)
            
            return {
                "id": response.id,
                "name": response.name,
                "bucket": response.bucket,
                "key": response.key,
                "size": response.size,
                "content_type": response.content_type,
                "checksum_sha256": response.checksum_sha256,
                "version_id": response.version_id if response.HasField("version_id") else None,
                "pipeline_id": response.pipeline_id if response.HasField("pipeline_id") else None,
                "execution_id": response.execution_id if response.HasField("execution_id") else None,
                "project_id": response.project_id if response.HasField("project_id") else None,
                "created_at": response.created_at.ToDatetime().isoformat() if response.HasField("created_at") else None,
                "updated_at": response.updated_at.ToDatetime().isoformat() if response.HasField("updated_at") else None
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error getting metadata: {e.code()} - {e.details()}")
            raise
    
    async def list_artifacts(
        self,
        project_id: Optional[str] = None,
        pipeline_id: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """
        List artifacts with optional filters.
        
        Args:
            project_id: Filter by project ID
            pipeline_id: Filter by pipeline ID
            
        Returns:
            List of artifact metadata dicts
        """
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            from app.grpc.generated import artifact_pb2
            
            request = artifact_pb2.ListArtifactsRequest(
                project_id=project_id or "",
                pipeline_id=pipeline_id or ""
            )
            
            metadata = (("x-api-key", self.api_key),)
            response = await self.stub.ListArtifacts(request, metadata=metadata)
            
            artifacts = []
            for artifact in response.artifacts:
                artifacts.append({
                    "id": artifact.id,
                    "name": artifact.name,
                    "bucket": artifact.bucket,
                    "key": artifact.key,
                    "size": artifact.size,
                    "content_type": artifact.content_type,
                    "checksum_sha256": artifact.checksum_sha256,
                    "created_at": artifact.created_at.ToDatetime().isoformat() if artifact.HasField("created_at") else None
                })
            
            return artifacts
        except grpc.RpcError as e:
            logger.error(f"gRPC error listing artifacts: {e.code()} - {e.details()}")
            raise
    
    async def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact.
        
        Args:
            artifact_id: Artifact ID to delete
            
        Returns:
            True if successful
        """
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            from app.grpc.generated import artifact_pb2
            
            request = artifact_pb2.DeleteArtifactRequest(artifact_id=artifact_id)
            
            metadata = (("x-api-key", self.api_key),)
            response = await self.stub.DeleteArtifact(request, metadata=metadata)
            
            return response.status == "deleted"
        except grpc.RpcError as e:
            logger.error(f"gRPC error deleting artifact: {e.code()} - {e.details()}")
            raise
    
    async def validate_checksum(self, artifact_id: str) -> Dict[str, Any]:
        """
        Validate artifact checksum integrity.
        
        Args:
            artifact_id: Artifact ID to validate
            
        Returns:
            Dict with validation results
        """
        if not self.stub:
            raise RuntimeError("Client not connected. Call connect() first.")
        
        try:
            from app.grpc.generated import artifact_pb2
            
            request = artifact_pb2.ValidateChecksumRequest(artifact_id=artifact_id)
            
            metadata = (("x-api-key", self.api_key),)
            response = await self.stub.ValidateChecksum(request, metadata=metadata)
            
            return {
                "valid": response.valid,
                "expected_checksum": response.expected_checksum,
                "actual_checksum": response.actual_checksum if response.HasField("actual_checksum") else None,
                "validation_time": response.validation_time.ToDatetime().isoformat() if response.HasField("validation_time") else None
            }
        except grpc.RpcError as e:
            logger.error(f"gRPC error validating checksum: {e.code()} - {e.details()}")
            raise
    
    async def close(self):
        """Close gRPC connection."""
        if self.channel:
            await self.channel.close()
            logger.info("Artifact Storage gRPC connection closed")

"""Global gRPC client management."""

from typing import Optional
import logging

from app.grpc.clients.artifact_storage_client import ArtifactStorageClient
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Global client instances
_artifact_storage_client: Optional[ArtifactStorageClient] = None


async def get_artifact_storage_client() -> ArtifactStorageClient:
    """
    Get or create the global Artifact Storage gRPC client.
    
    Returns:
        Connected ArtifactStorageClient instance
    """
    global _artifact_storage_client
    
    if _artifact_storage_client is None:
        settings = get_settings()
        _artifact_storage_client = ArtifactStorageClient(
            host=settings.artifact_storage_host,
            port=settings.artifact_storage_grpc_port
        )
        await _artifact_storage_client.connect()
        logger.info("Artifact Storage gRPC client initialized")
    
    return _artifact_storage_client


async def close_artifact_storage_client():
    """Close the Artifact Storage gRPC client."""
    global _artifact_storage_client
    
    if _artifact_storage_client is not None:
        await _artifact_storage_client.close()
        _artifact_storage_client = None
        logger.info("Artifact Storage gRPC client closed")

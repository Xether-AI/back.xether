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
    
    # If client doesn't exist or isn't connected, initialize it
    if _artifact_storage_client is None or _artifact_storage_client.stub is None:
        settings = get_settings()
        client = ArtifactStorageClient(
            host=settings.artifact_storage_host,
            port=settings.artifact_storage_grpc_port,
            api_key=settings.artifact_storage_api_key
        )
        try:
            await client.connect()
            _artifact_storage_client = client
            logger.info("Artifact Storage gRPC client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Artifact Storage gRPC client: {e}")
            _artifact_storage_client = None
            raise
    
    return _artifact_storage_client


async def close_artifact_storage_client():
    """Close the Artifact Storage gRPC client."""
    global _artifact_storage_client
    
    if _artifact_storage_client is not None:
        await _artifact_storage_client.close()
        _artifact_storage_client = None
        logger.info("Artifact Storage gRPC client closed")

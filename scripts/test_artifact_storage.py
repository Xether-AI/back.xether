#!/usr/bin/env python3
"""Test script to verify Artifact Storage gRPC integration."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.grpc_clients import get_artifact_storage_client


async def test_artifact_storage():
    """Test Artifact Storage gRPC client."""
    print("Testing Artifact Storage gRPC connection...")
    
    try:
        # Get client (will connect)
        client = await get_artifact_storage_client()
        print("✅ Successfully connected to Artifact Storage gRPC")
        
        # Test getting upload URL
        print("\nTesting upload URL generation...")
        result = await client.get_upload_url(
            name="test-artifact.txt",
            bucket="test-bucket",
            key="test/artifact.txt",
            content_type="text/plain",
            expires_in_seconds=3600,
            project_id="test-project"
        )
        
        print(f"✅ Upload URL generated:")
        print(f"   Artifact ID: {result['artifact_id']}")
        print(f"   Upload URL: {result['upload_url'][:80]}...")
        
        # Test listing artifacts
        print("\nTesting artifact listing...")
        artifacts = await client.list_artifacts(project_id="test-project")
        print(f"✅ Listed {len(artifacts)} artifacts")
        
        print("\n✅ All Artifact Storage tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Artifact Storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("=" * 60)
    print("Artifact Storage gRPC Integration Test")
    print("=" * 60)
    print("\nMake sure Artifact Storage is running:")
    print("  cd 'Artifact Storage'")
    print("  docker-compose up -d")
    print("  OR")
    print("  go run cmd/server/main.go")
    print("\n" + "=" * 60 + "\n")
    
    success = await test_artifact_storage()
    
    if success:
        print("\n🎉 Artifact Storage gRPC integration is working!")
        sys.exit(0)
    else:
        print("\n⚠️  Artifact Storage integration test failed.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

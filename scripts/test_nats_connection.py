#!/usr/bin/env python3
"""Test script to verify NATS connection and event publishing."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.events import get_event_bus


async def test_nats_connection():
    """Test NATS connection and basic operations."""
    print("Testing NATS connection...")
    
    try:
        # Get event bus (will connect to NATS)
        event_bus = await get_event_bus()
        print("✅ Successfully connected to NATS")
        
        # Test publishing an event
        test_data = {
            "test": "message",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        await event_bus.publish("backend.test.event", test_data)
        print("✅ Successfully published test event to 'backend.test.event'")
        
        # Test subscribing (just verify it doesn't error)
        async def test_callback(data):
            print(f"📨 Received test message: {data}")
        
        await event_bus.subscribe("backend.test.>", test_callback, durable_name="test-consumer")
        print("✅ Successfully subscribed to 'backend.test.>' subject")
        
        # Wait a bit to see if we receive our own message
        print("\nWaiting 2 seconds for messages...")
        await asyncio.sleep(2)
        
        print("\n✅ All NATS tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ NATS test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("=" * 60)
    print("NATS Connection Test")
    print("=" * 60)
    print("\nMake sure NATS is running:")
    print("  docker-compose up -d nats")
    print("  OR")
    print("  nats-server -js")
    print("\n" + "=" * 60 + "\n")
    
    success = await test_nats_connection()
    
    if success:
        print("\n🎉 NATS integration is working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️  NATS integration test failed. Check the error above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

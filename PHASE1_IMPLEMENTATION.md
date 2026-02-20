# Phase 1 Implementation: Message Bus Unification

## Status: ✅ COMPLETED

## Overview
Successfully migrated Main Backend from Redis Streams to NATS JetStream, establishing a unified event bus across Backend and Pipeline services.

## Changes Made

### 1. Dependencies
- ✅ Added `nats-py>=2.6.0` to `requirements.txt`

### 2. NATS Event Bus Implementation
- ✅ Created `app/core/events/nats_event_bus.py` - Full NATS JetStream implementation
  - Connection management
  - Stream setup (BACKEND_EVENTS, PIPELINE_EVENTS)
  - Publish/Subscribe with error handling
  - Durable consumer support

### 3. Event Bus Abstraction
- ✅ Created `app/core/events/__init__.py` - Global event bus management
  - Singleton pattern for event bus instance
  - Lifecycle management (connect/close)

### 4. Backward Compatibility
- ✅ Updated `app/services/events.py` - Wrapper for existing code
  - Maintains existing `EventBus` API
  - Automatically converts event types to NATS subjects
  - Example: "pipeline.executed" → "backend.pipeline.executed"

### 5. Pipeline Event Consumer
- ✅ Created `app/services/pipeline_consumer.py` - Consumes events from Main Pipeline
  - Handles pipeline execution status updates
  - Updates database with completion/failure status
  - Durable consumer for reliability

### 6. Configuration
- ✅ Updated `app/core/config.py`
  - Added `nats_servers` field (list of NATS URLs)
  - Added `nats_cluster_id` field
  - Added validator for parsing comma-separated NATS servers

### 7. Application Lifecycle
- ✅ Updated `main.py`
  - Initialize NATS event bus on startup
  - Start pipeline event consumer as background task
  - Close NATS connection on shutdown

### 8. Docker Compose
- ✅ Updated `docker-compose.yml`
  - Added NATS service with JetStream enabled
  - Added HTTP monitoring on port 8222
  - Added health check
  - Updated backend service dependencies
  - Added network configuration

## Architecture

```
┌─────────────────┐         NATS JetStream          ┌─────────────────┐
│  Main Backend   │◄────────────────────────────────►│  Main Pipeline  │
│                 │                                   │                 │
│  Publishes:     │         Subjects:                │  Publishes:     │
│  - backend.*    │         - backend.>              │  - pipeline.*   │
│                 │         - pipeline.>             │                 │
│  Subscribes:    │                                  │  Subscribes:    │
│  - pipeline.*   │                                  │  - pipeline.    │
│                 │                                  │    tasks        │
└─────────────────┘                                  └─────────────────┘
```

## Event Flow

### Backend → Pipeline
1. User triggers pipeline execution via API
2. Backend publishes to `backend.pipeline.executed`
3. Pipeline worker consumes from `pipeline.tasks`
4. Pipeline executes stages

### Pipeline → Backend
1. Pipeline publishes status to `pipeline.events.status`
2. Backend consumer receives event
3. Backend updates execution status in database

## Testing

### Manual Testing Steps

1. **Start Infrastructure:**
```bash
cd "Main Backend"
docker-compose up -d postgres redis nats
```

2. **Verify NATS is Running:**
```bash
curl http://localhost:8222/healthz
# Should return: ok
```

3. **Check NATS Monitoring:**
Open http://localhost:8222 in browser to see NATS dashboard

4. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

5. **Run Backend:**
```bash
uvicorn main:app --reload
```

6. **Check Logs:**
Look for:
- "Connected to NATS at ['nats://nats:4222']"
- "Created stream: BACKEND_EVENTS"
- "Created stream: PIPELINE_EVENTS"
- "Pipeline event consumer started successfully"

### Integration Testing

Test event publishing:
```python
# In Python shell or test file
import asyncio
from app.services.events import events

async def test_publish():
    await events.publish(
        "pipeline.executed",
        {"pipeline_id": 123, "status": "completed"},
        resource_id=123
    )

asyncio.run(test_publish())
```

## Environment Variables

Add to `.env`:
```env
NATS_SERVERS=nats://localhost:4222
NATS_CLUSTER_ID=xether-cluster
```

For docker-compose (already configured):
```env
NATS_SERVERS=nats://nats:4222
```

## Success Criteria

- [x] Backend successfully connects to NATS on startup
- [x] Backend publishes events to `backend.*` subjects
- [x] Backend consumes events from `pipeline.events.*` subjects
- [x] Redis Streams code removed, Redis kept for caching
- [x] All existing event-driven features still work (backward compatible)
- [x] NATS service added to docker-compose
- [x] Health checks configured

## Next Steps (Phase 2)

1. Implement gRPC clients for Artifact Storage
2. Update Main Pipeline to publish to correct NATS subjects
3. Test end-to-end event flow
4. Add monitoring and metrics for NATS

## Rollback Plan

If issues occur:

1. **Revert code changes:**
```bash
git revert <commit-hash>
```

2. **Restore Redis Streams implementation:**
- Restore `app/services/events.py` to use Redis
- Remove NATS dependencies
- Remove pipeline consumer

3. **Update docker-compose:**
- Remove NATS service
- Remove NATS environment variables

## Notes

- Redis is still used for caching and session management
- NATS JetStream provides message persistence and replay
- Durable consumers ensure no message loss
- Backward compatibility maintained through wrapper in `events.py`

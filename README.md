# Xether AI - Main Backend

## Overview

The main backend service for Xether AI, providing the core API layer, authentication, authorization, and metadata management for the enterprise data infrastructure platform.

## Responsibilities

### 1. Authentication & Authorization

- User authentication via OAuth2 and JWT
- Role-based access control (RBAC)
- Team and project-level permissions
- API key management for programmatic access

### 2. Dataset Registry

- Central metadata registry for all datasets
- Dataset versioning and lineage tracking
- Schema validation and statistics storage
- Immutable historical snapshots

### 3. User & Team Management

- User account management
- Team and organization structure
- Project workspace management
- Access policies and governance

### 4. API Gateway

- RESTful API for external clients
- Request routing and validation
- Rate limiting and quota management
- API documentation (OpenAPI/Swagger)

### 5. Orchestration Coordination

- Pipeline execution triggers
- Job scheduling and monitoring
- Event publishing to message bus
- Status tracking and notifications

## Architecture

### Communication Protocols

- **REST API**: External client communication, CRUD operations (FastAPI)
- **gRPC**: Internal service-to-service communication foundation initialized.
- **Event Bus**: Redis Streams for asynchronous event publishing (datasets, pipelines).

### Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ASGI Server**: Uvicorn + Gunicorn (production)
- **ORM**: SQLAlchemy 2.0 (Async)
- **Database**: PostgreSQL 15+
- **Migrations**: Alembic
- **Auth**: OAuth2 + JWT (Internal implementation)
- **Cache**: Redis 7+
- **Async Tasks**: Celery with Redis backend
- **Observability**: Prometheus metrics + Structured JSON Logging

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Redis (Optional if running locally without Docker)
- PostgreSQL (Optional if running locally without Docker)

### Development Setup

1. **Clone the repository**
2. **Setup virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Start Infrastructure**:
   ```bash
   docker compose up -d
   ```
4. **Run Migrations**:
   ```bash
   alembic upgrade head
   ```
5. **Start Application**:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Structure

```
/api/v1
├── /auth          # Authentication & Token management
├── /users         # User profiles & Admin management
├── /teams         # Team & Membership management
├── /projects      # Project workspaces & RBAC
├── /datasets      # Dataset registry & Versioning
├── /pipelines     # Pipeline config & Execution triggering
└── /audit-logs    # System audit trails
```

## Testing

Run the full test suite with coverage:

```bash
pytest --cov=app tests/
```

## Status

✅ **Phase 7 Complete** - Core API, Auth, Integration, and Testing (76% coverage) implemented.
🚀 **Phase 8/9 in Progress** - Documentation and Production preparation.

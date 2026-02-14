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

- **REST API**: External client communication, CRUD operations
- **gRPC**: Internal service-to-service communication (ML services, pipeline workers)
- **Event Bus**: Asynchronous pipeline orchestration (Kafka/RabbitMQ/NATS)

### Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ASGI Server**: Uvicorn + Gunicorn (production)
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 15+
- **Migrations**: Alembic
- **Auth**: OAuth2 + JWT (Keycloak or Auth0)
- **Cache**: Redis 7+
- **Async Tasks**: Celery or Dramatiq
- **Message Queue**: Kafka or NATS (event-driven orchestration)
- **Internal Communication**: gRPC client (to ML services, pipeline workers)

### Why FastAPI?

- **Async support**: Native async/await for high concurrency
- **Auto-documentation**: OpenAPI/Swagger generated automatically
- **Type safety**: Pydantic models for validation and serialization
- **Performance**: Comparable to Node.js and Go for I/O-bound workloads
- **Clean boundaries**: Easy to maintain service separation

### Critical Design Rule

**This service must never process large datasets.**

It manages metadata and coordinates. Nothing more. If you let it touch heavy data, you deserve the scaling pain you'll get.

## Design Principles

- **Explicit over implicit**: Clear contracts and interfaces
- **Stateless services**: Horizontal scalability
- **Fail-fast validation**: Early error detection
- **Audit everything**: Complete lineage and compliance trails
- **Enterprise-grade defaults**: Security, reliability, observability

## Getting Started

> **Note**: This service is currently in the planning/initialization phase.

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Kafka or NATS (message broker)
- MinIO or AWS S3 access (for dataset metadata references)

### Development Setup

```bash
# To be implemented
```

## API Structure (Planned)

```
/api/v1
├── /auth          # Authentication endpoints
├── /users         # User management
├── /teams         # Team and organization management
├── /projects      # Project workspaces
├── /datasets      # Dataset registry and metadata
├── /pipelines     # Pipeline configuration and execution
├── /jobs          # Job status and monitoring
└── /audit         # Audit logs and lineage
```

## Related Components

- **[Main Pipeline](../main%20pipeline)**: High-performance data processing engine
- **ML Services**: AI-powered data operations (separate microservices)
- **[Website](../website)**: Marketing and product website
- **[Docs](../docs)**: Developer documentation and API references

## Status

🚧 **In Development** - Architecture and initial implementation in progress.

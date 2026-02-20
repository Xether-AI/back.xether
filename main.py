"""Main FastAPI application."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import get_settings, setup_logging
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.api import api_router
from app.api.middleware import RequestIDMiddleware
from app.api.v1.endpoints import health
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.redis import close_redis, init_redis
from app.core.events import get_event_bus, close_event_bus
from app.core.grpc_clients import get_artifact_storage_client, close_artifact_storage_client
from app.services.pipeline_consumer import start_consumer
import asyncio
import logging

# Initialize logging
setup_logging()

settings = get_settings()

# Get logger for this module
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    await init_redis()
    
    # Initialize NATS event bus and start consumer
    try:
        await get_event_bus()
        asyncio.create_task(start_consumer())
    except Exception as e:
        logger.error(f"Failed to initialize NATS event bus: {e}")
    
    # Initialize Artifact Storage gRPC client
    try:
        await get_artifact_storage_client()
    except Exception as e:
        logger.warning(f"Failed to initialize Artifact Storage client: {e}")
        logger.warning("Artifact endpoints will not be available")
    
    yield
    
    # Shutdown
    await close_artifact_storage_client()
    await close_event_bus()
    await close_redis()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
Xether AI Backend - The Central Control Plane for Distributed AI Workflows.

### Features
* **Auth**: Secure JWT and API Key based authentication.
* **Teams & RBAC**: Advanced team management with role-based access control.
* **Datasets**: Reliable dataset registration and versioning.
* **Pipelines**: Scalable ML pipeline orchestration and execution tracking.
* **Observability**: Structured logging, Prometheus metrics, and advanced health checks.
""",
    version=settings.app_version,
    contact={
        "name": "Xether AI Team",
        "url": "https://xether.ai",
        "email": "support@xether.ai",
    },
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan,
)


# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Observation & Security Middleware
app.add_middleware(RequestIDMiddleware)
from app.api.middleware import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware)


# Setup Prometheus
Instrumentator().instrument(app).expose(app)

# Error Handlers
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.exceptions import XetherError
from app.core.logging import get_logger

logger = get_logger(__name__)

@app.exception_handler(XetherError)
async def xether_exception_handler(request: Request, exc: XetherError):
    """Handle custom system exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "code": exc.code,
                "details": exc.details,
                "request_id": getattr(request.state, "request_id", None)
            }
        },
    )

@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    """Handle unhandled system exceptions."""
    logger.exception(f"Unhandled exception occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An unexpected error occurred. Please contact support.",
                "code": "INTERNAL_SERVER_ERROR",
                "request_id": getattr(request.state, "request_id", None)
            }
        },
    )

# Include API routers

app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": settings.docs_url,
    }


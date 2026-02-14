"""Main FastAPI application."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import get_settings, setup_logging
from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.redis import close_redis, init_redis

# Initialize logging
setup_logging()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    await init_redis()
    yield
    # Shutdown
    await close_redis()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
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

# Include API router
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for liveness probe."""
    return {"status": "healthy"}


@app.get("/health/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness check endpoint."""
    # TODO: Add database and Redis connectivity checks
    return {"status": "ready"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": settings.docs_url,
    }

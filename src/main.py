"""Main FastAPI application."""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import api_router
from src.core.config import settings
from src.core.exception_handlers import register_exception_handlers
from src.middleware.rate_limiting import RateLimitMiddleware
from src.schemas.common import ApiResponse, HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting Sales Dashboard API...")
    yield
    # Shutdown
    print("Shutting down Sales Dashboard API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Sales Dashboard API - A modern FastAPI backend for sales analytics",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add rate limiting middleware
    # Note: Add this AFTER CORS to ensure rate limit headers are included in CORS responses
    app.add_middleware(RateLimitMiddleware)

    # Register exception handlers
    register_exception_handlers(app)

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Health check endpoint
    @app.get("/health", response_model=ApiResponse[HealthResponse], tags=["Health"])
    async def health_check():
        """
        Health check endpoint.

        Returns the current status and version of the API.
        This endpoint is exempt from rate limiting.
        """
        health_data = HealthResponse(
            status="ok",
            version=settings.VERSION,
            timestamp=datetime.utcnow()
        )
        return ApiResponse.success_response(health_data)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

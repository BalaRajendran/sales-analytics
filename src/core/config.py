"""Application configuration."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    PROJECT_NAME: str = "Sales Dashboard API"
    VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # Server
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="List of allowed origins for CORS",
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./sales_dashboard.db",
        description="Database connection URL",
    )
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, description="Database pool timeout (seconds)")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, description="Database pool recycle time (seconds)")

    # Redis Cache
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )
    REDIS_PASSWORD: str | None = Field(default=None, description="Redis password")
    REDIS_MAX_CONNECTIONS: int = Field(default=50, description="Redis max connections")

    # GraphQL
    GRAPHQL_DEBUG: bool = Field(default=True, description="Enable GraphQL debug mode")
    GRAPHQL_MAX_DEPTH: int = Field(default=10, description="Maximum GraphQL query depth")
    GRAPHQL_MAX_COMPLEXITY: int = Field(default=1000, description="Maximum GraphQL query complexity")
    GRAPHQL_ENABLE_PLAYGROUND: bool = Field(default=True, description="Enable GraphQL playground")

    # Celery (Background Tasks)
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL",
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        description="Celery result backend URL",
    )

    # Cache TTL (Time To Live in seconds)
    CACHE_TTL_DASHBOARD: int = Field(default=60, description="Dashboard overview cache TTL")
    CACHE_TTL_PRODUCTS: int = Field(default=300, description="Product insights cache TTL")
    CACHE_TTL_CUSTOMERS: int = Field(default=600, description="Customer analytics cache TTL")
    CACHE_TTL_TRENDS: int = Field(default=180, description="Trends cache TTL")
    CACHE_TTL_REALTIME: int = Field(default=30, description="Realtime metrics cache TTL")

    # Performance
    ENABLE_COMPRESSION: bool = Field(default=True, description="Enable response compression")
    ENABLE_QUERY_LOGGING: bool = Field(default=False, description="Enable database query logging")
    COMPRESSION_MINIMUM_SIZE: int = Field(default=1000, description="Minimum size for compression")
    COMPRESSION_LEVEL: int = Field(default=6, description="Compression level (1-9)")

    # Monitoring
    ENABLE_PROMETHEUS: bool = Field(default=True, description="Enable Prometheus metrics")
    PROMETHEUS_PORT: int = Field(default=9090, description="Prometheus metrics port")

    # Security
    SECRET_KEY: str = Field(
        default="change-me-in-production-please-use-strong-secret-key",
        description="Secret key for JWT token generation",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Rate Limiting Settings
    RATE_LIMIT_ENABLED: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Default rate limit (requests per minute)"
    )
    RATE_LIMIT_BULK_OPERATIONS: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Rate limit for bulk operations"
    )


settings = Settings()

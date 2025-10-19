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
        default=100,
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

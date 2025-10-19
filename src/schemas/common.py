"""
Common schemas and base classes for URL Shortener API.

Contains shared schemas, base classes, and common validation patterns.
"""

from datetime import datetime
from typing import Annotated, Any, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

# Common query parameter type definitions
LimitQuery = Annotated[int, Query(ge=1, le=1000, description="Maximum number of items to return")]
OffsetQuery = Annotated[int, Query(ge=0, description="Number of items to skip")]


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for models with timestamps."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    limit: Annotated[int, Field(ge=1, le=1000, description="Maximum number of items to return")] = 100
    offset: Annotated[int, Field(ge=0, description="Number of items to skip")] = 0


class PaginatedResponse[T](BaseSchema):
    """Base response for paginated results."""

    items: list[T] = Field(..., description="List of items")
    total: Annotated[int, Field(ge=0)] = Field(..., description="Total number of items")
    limit: Annotated[int, Field(ge=1)] = Field(..., description="Items per page")
    offset: Annotated[int, Field(ge=0)] = Field(..., description="Current offset")
    has_more: bool = Field(..., description="Whether there are more items")


class ErrorDetail(BaseSchema):
    """Error detail schema."""

    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    field: str | None = Field(None, description="Field that caused the error")
    code: str | None = Field(None, description="Error code")


class ErrorResponse(BaseSchema):
    """Standard error response schema."""

    detail: str = Field(..., description="Error message")
    type: str | None = Field(None, description="Error type")
    code: str | None = Field(None, description="Error code")


class SuccessResponse(BaseSchema):
    """Standard success response schema."""

    success: bool = Field(True, description="Success status")
    message: str = Field(..., description="Success message")
    data: Any | None = Field(None, description="Optional response data")


class ApiResponse[T](BaseSchema):
    """Standardized API response wrapper for all endpoints."""

    success: bool = Field(..., description="Whether the request was successful")
    data: T | None = Field(None, description="Response data (null on error)")
    error_code: str | None = Field(None, description="Error code if request failed")
    error_message: str | None = Field(None, description="Error message if request failed")

    @staticmethod
    def success_response(data: T) -> "ApiResponse[T]":
        """Create a successful response."""
        return ApiResponse(
            success=True,
            data=data,
            error_code=None,
            error_message=None,
        )

    @staticmethod
    def error_response(error_code: str, error_message: str, data: Any = None) -> "ApiResponse":
        """Create an error response."""
        return ApiResponse(
            success=False,
            data=data,
            error_code=error_code,
            error_message=error_message,
        )


class ApiErrorResponse(BaseSchema):
    """Standardized API error response."""

    success: bool = Field(False, description="Always false for error responses")
    data: dict[str, Any] | None = Field(None, description="Additional error data (e.g., validation errors)")
    error_code: str = Field(..., description="Machine-readable error code")
    error_message: str = Field(..., description="Human-readable error message")


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current timestamp")


class SearchParams(BaseModel):
    """Search parameters for endpoints with search functionality."""

    q: str | None = Field(None, min_length=1, max_length=255, description="Search query")
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order (asc/desc)")


class DateRangeParams(BaseModel):
    """Date range filter parameters."""

    from_date: datetime | None = Field(None, description="Start date (inclusive)")
    to_date: datetime | None = Field(None, description="End date (inclusive)")

    def validate_date_range(self) -> "DateRangeParams":
        """Validate that from_date is before to_date."""
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValueError("from_date must be before to_date")
        return self

"""Custom exceptions for the URL Shortener API.

Defines custom exception classes with standardized error codes
for consistent error handling across the application.
"""

from typing import Any


class ErrorCode:
    """Standard error codes for API responses."""

    # Client errors (4xx)
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class APIError(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        message: str,
        error_code: str = ErrorCode.INTERNAL_ERROR,
        status_code: int = 500,
        data: dict[str, Any] | None = None,
    ):
        """Initialize API error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            status_code: HTTP status code
            data: Additional error data
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.data = data or {}
        super().__init__(self.message)


class NotFoundError(APIError):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", data: dict[str, Any] | None = None):
        """Initialize not found error."""
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            status_code=404,
            data=data,
        )


class ValidationError(APIError):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        data: dict[str, Any] | None = None,
    ):
        """Initialize validation error."""
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            data=data,
        )


class ConflictError(APIError):
    """Exception raised for resource conflicts (e.g., duplicate short code)."""

    def __init__(
        self,
        message: str = "Resource conflict",
        data: dict[str, Any] | None = None,
    ):
        """Initialize conflict error."""
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFLICT,
            status_code=409,
            data=data,
        )


class BadRequestError(APIError):
    """Exception raised for bad requests."""

    def __init__(
        self,
        message: str = "Bad request",
        data: dict[str, Any] | None = None,
    ):
        """Initialize bad request error."""
        super().__init__(
            message=message,
            error_code=ErrorCode.BAD_REQUEST,
            status_code=400,
            data=data,
        )


class UnauthorizedError(APIError):
    """Exception raised for unauthorized access."""

    def __init__(
        self,
        message: str = "Unauthorized",
        data: dict[str, Any] | None = None,
    ):
        """Initialize unauthorized error."""
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401,
            data=data,
        )


class ForbiddenError(APIError):
    """Exception raised for forbidden access."""

    def __init__(
        self,
        message: str = "Forbidden",
        data: dict[str, Any] | None = None,
    ):
        """Initialize forbidden error."""
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=403,
            data=data,
        )


class RateLimitError(APIError):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60,
        data: dict[str, Any] | None = None,
    ):
        """Initialize rate limit error."""
        error_data = data or {}
        error_data["retry_after"] = retry_after
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            data=error_data,
        )


class InternalServerError(APIError):
    """Exception raised for internal server errors."""

    def __init__(
        self,
        message: str = "Internal server error",
        data: dict[str, Any] | None = None,
    ):
        """Initialize internal server error."""
        super().__init__(
            message=message,
            error_code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
            data=data,
        )


class DatabaseError(APIError):
    """Exception raised for database errors."""

    def __init__(
        self,
        message: str = "Database error",
        data: dict[str, Any] | None = None,
    ):
        """Initialize database error."""
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            data=data,
        )


class ServiceUnavailableError(APIError):
    """Exception raised when service is unavailable."""

    def __init__(
        self,
        message: str = "Service unavailable",
        data: dict[str, Any] | None = None,
    ):
        """Initialize service unavailable error."""
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            status_code=503,
            data=data,
        )

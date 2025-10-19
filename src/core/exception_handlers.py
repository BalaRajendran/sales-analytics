"""Exception handlers for FastAPI application.

Centralizes all exception handling logic to ensure consistent
error responses across the application.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions import APIError
from src.schemas.common import ApiErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI application.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        """Handle custom API errors.

        Converts APIError exceptions into standardized JSON responses.

        Args:
            request: FastAPI request object
            exc: APIError exception instance

        Returns:
            JSONResponse with standardized error format
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiErrorResponse(
                success=False,
                data=exc.data if exc.data else None,
                error_code=exc.error_code,
                error_message=exc.message,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors.

        Converts Pydantic validation errors into standardized format
        with detailed field-level error information.

        Args:
            request: FastAPI request object
            exc: RequestValidationError from Pydantic

        Returns:
            JSONResponse with validation error details
        """
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ApiErrorResponse(
                success=False,
                data={"validation_errors": errors},
                error_code="VALIDATION_ERROR",
                error_message="Request validation failed",
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions.

        Catches any unhandled exceptions and returns a generic error response
        to prevent exposing internal implementation details.

        Args:
            request: FastAPI request object
            exc: Exception instance

        Returns:
            JSONResponse with generic error message
        """
        # Log the error (in production, use proper logging)
        # TODO: Replace with proper logging framework
        import traceback
        print(f"Unexpected error: {exc}")
        print(traceback.format_exc())

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiErrorResponse(
                success=False,
                data=None,
                error_code="INTERNAL_ERROR",
                error_message="An unexpected error occurred",
            ).model_dump(),
        )


def configure_error_responses(app: FastAPI) -> None:
    """Configure custom error responses for OpenAPI documentation.

    Updates the OpenAPI schema with standardized error response formats.

    Args:
        app: FastAPI application instance
    """
    # Add custom responses to OpenAPI schema
    custom_responses = {
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "error_code": "BAD_REQUEST",
                        "error_message": "Invalid request parameters",
                    }
                }
            },
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "error_code": "NOT_FOUND",
                        "error_message": "Resource not found",
                    }
                }
            },
        },
        409: {
            "description": "Conflict",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "error_code": "CONFLICT",
                        "error_message": "Resource conflict",
                    }
                }
            },
        },
        422: {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": {
                            "validation_errors": [
                                {
                                    "field": "body.url",
                                    "message": "Invalid URL format",
                                    "type": "value_error",
                                }
                            ]
                        },
                        "error_code": "VALIDATION_ERROR",
                        "error_message": "Request validation failed",
                    }
                }
            },
        },
        429: {
            "description": "Too Many Requests",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": {
                            "retry_after": 60,
                            "current_count": 101,
                            "limit": 100,
                        },
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "error_message": "Rate limit exceeded. Please try again in 60 seconds.",
                    }
                }
            },
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "data": None,
                        "error_code": "INTERNAL_ERROR",
                        "error_message": "An unexpected error occurred",
                    }
                }
            },
        },
    }

    # Update app responses (this will be included in OpenAPI schema)
    if not hasattr(app, "responses"):
        app.responses = custom_responses
    else:
        app.responses.update(custom_responses)

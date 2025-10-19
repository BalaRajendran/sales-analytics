"""
Rate Limiting Middleware for URL Shortener API.

Implements in-memory rate limiting with configurable limits per endpoint.
Can be extended to use Redis for distributed rate limiting.
"""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.config import settings
from src.schemas.common import ApiErrorResponse


class InMemoryRateLimiter:
    """Simple in-memory rate limiter using sliding window algorithm."""

    def __init__(self):
        # Store: {client_id: {endpoint: [(timestamp, count)]}}
        self._requests: Dict[str, Dict[str, list[Tuple[float, int]]]] = defaultdict(lambda: defaultdict(list))
        self._cleanup_interval = 60  # Cleanup old entries every 60 seconds
        self._last_cleanup = time.time()

    def is_allowed(self, client_id: str, endpoint: str, limit: int, window: int) -> Tuple[bool, int, int]:
        """
        Check if request is allowed under rate limit.

        Args:
            client_id: Unique client identifier
            endpoint: API endpoint path
            limit: Maximum requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (is_allowed, current_count, reset_time)
        """
        current_time = time.time()
        window_start = current_time - window

        # Cleanup old requests periodically
        if current_time - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_requests(window_start)
            self._last_cleanup = current_time

        # Get requests for this client and endpoint
        requests = self._requests[client_id][endpoint]

        # Remove requests outside the current window
        requests[:] = [(ts, count) for ts, count in requests if ts > window_start]

        # Count total requests in window
        current_count = sum(count for _, count in requests)

        # Check if limit exceeded
        if current_count >= limit:
            # Calculate when the oldest request will expire
            if requests:
                oldest_ts = requests[0][0]
                reset_time = int(oldest_ts + window - current_time)
            else:
                reset_time = window
            return False, current_count, reset_time

        # Add current request
        requests.append((current_time, 1))

        return True, current_count + 1, 0

    def _cleanup_old_requests(self, cutoff_time: float):
        """Remove requests older than cutoff time."""
        for client_requests in self._requests.values():
            for endpoint, requests in list(client_requests.items()):
                requests[:] = [(ts, count) for ts, count in requests if ts > cutoff_time]
                if not requests:
                    del client_requests[endpoint]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for API rate limiting."""

    def __init__(self, app):
        super().__init__(app)
        self.limiter = InMemoryRateLimiter()

        # Default rate limit: 100 requests per minute
        self.default_limit = 100
        self.default_window = 60  # seconds

        # Per-endpoint rate limits (requests per minute)
        self.endpoint_limits = {
            "/api/v1/urls/": 30,  # URL creation
            "/api/v1/urls/bulk": 5,  # Bulk operations
            "/health": 1000,  # Health checks
        }

        # Exempt paths (no rate limiting)
        self.exempt_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting checks."""
        # Skip rate limiting in test environment
        if settings.DEBUG and settings.ENVIRONMENT == "testing":
            return await call_next(request)

        # Skip rate limiting for exempt paths
        if self._is_exempt_path(request.url.path):
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Get endpoint-specific limit or use default
        endpoint = request.url.path
        limit = self.endpoint_limits.get(endpoint, self.default_limit)

        # Check rate limit
        is_allowed, current_count, reset_time = self.limiter.is_allowed(
            client_id,
            endpoint,
            limit,
            self.default_window
        )

        if not is_allowed:
            # Rate limit exceeded - return standardized error response
            error_response = ApiErrorResponse(
                success=False,
                data={
                    "retry_after": reset_time,
                    "current_count": current_count,
                    "limit": limit,
                },
                error_code="RATE_LIMIT_EXCEEDED",
                error_message=f"Rate limit exceeded. Please try again in {reset_time} seconds.",
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=error_response.model_dump(),
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + reset_time),
                    "Retry-After": str(reset_time),
                },
            )

        # Request allowed - proceed
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = max(0, limit - current_count)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.default_window)

        return response

    def _get_client_id(self, request: Request) -> str:
        """
        Get unique client identifier for rate limiting.

        Priority: user_id > api_key > client_ip > user_agent
        """
        # 1. Try to get user ID from request state (if authentication is implemented)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # 2. Try to get API key from headers (if implemented)
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key}"

        # 3. Use client IP address
        # Handle both direct connections and proxied requests
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP from X-Forwarded-For header
            client_ip = forwarded_for.split(",")[0].strip()
        elif request.client:
            client_ip = request.client.host
        else:
            client_ip = "unknown"

        if client_ip != "unknown":
            return f"ip:{client_ip}"

        # 4. Fallback to user agent hash
        user_agent = request.headers.get("User-Agent", "unknown")
        return f"ua:{hash(user_agent)}"

    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from rate limiting."""
        return any(path.startswith(exempt_path) for exempt_path in self.exempt_paths)


# Rate limiting decorator for specific endpoints
def rate_limit(limit: int = 100, window: int = 60):
    """
    Decorator to add rate limiting to specific endpoints.

    Args:
        limit: Maximum number of requests
        window: Time window in seconds

    Example:
        @router.post("/urls/")
        @rate_limit(limit=10, window=60)
        async def create_url(...):
            pass
    """
    def decorator(func):
        # This is a placeholder - actual implementation would use
        # slowapi or similar for per-endpoint rate limiting
        return func
    return decorator

"""Middleware for the URL Shortener API."""

from src.middleware.rate_limiting import RateLimitMiddleware

__all__ = ["RateLimitMiddleware"]

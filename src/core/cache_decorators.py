"""
Cache decorator utilities.

Provides decorators for easy caching of function results.
"""

import functools
import hashlib
import json
import logging
from typing import Any, Callable, Optional

from src.core.cache import cache_manager

logger = logging.getLogger(__name__)


def generate_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        prefix: Cache key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Generated cache key
    """
    # Create a string representation of args and kwargs
    arg_str = json.dumps(
        {"args": [str(arg) for arg in args], "kwargs": {k: str(v) for k, v in kwargs.items()}},
        sort_keys=True,
    )

    # Hash the arguments for a shorter, consistent key
    arg_hash = hashlib.md5(arg_str.encode()).hexdigest()

    return f"{prefix}:{arg_hash}"


def cached(
    key_prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable[..., str]] = None,
):
    """
    Decorator to cache function results.

    Args:
        key_prefix: Prefix for cache keys
        ttl: Time-to-live in seconds (None for no expiration)
        key_builder: Optional custom function to build cache key from args

    Example:
        @cached(key_prefix="user_profile", ttl=300)
        async def get_user_profile(user_id: str) -> dict:
            return {"id": user_id, "name": "John"}

        @cached(
            key_prefix="product",
            ttl=600,
            key_builder=lambda product_id, period: f"product:{product_id}:{period}"
        )
        async def get_product_metrics(product_id: str, period: str) -> dict:
            return {"revenue": 1000}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = generate_cache_key(key_prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value

            # Cache miss - call the function
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_manager.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


def cache_result(ttl: Optional[int] = None):
    """
    Simple decorator to cache function results with automatic key generation.

    Args:
        ttl: Time-to-live in seconds (None for no expiration)

    Example:
        @cache_result(ttl=300)
        async def expensive_calculation(x: int, y: int) -> int:
            return x * y
    """

    def decorator(func: Callable) -> Callable:
        key_prefix = f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = generate_cache_key(key_prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value

            # Cache miss - call the function
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_manager.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


def invalidate_on_change(cache_patterns: list[str]):
    """
    Decorator to invalidate cache patterns after function execution.

    Useful for mutations that should clear related caches.

    Args:
        cache_patterns: List of cache key patterns to invalidate

    Example:
        @invalidate_on_change(["product:*", "dashboard:*"])
        async def update_product(product_id: str, data: dict) -> Product:
            # Update product in database
            return updated_product
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Execute the function
            result = await func(*args, **kwargs)

            # Invalidate cache patterns
            for pattern in cache_patterns:
                deleted = await cache_manager.delete_pattern(pattern)
                logger.info(f"Invalidated {deleted} keys matching pattern: {pattern}")

            return result

        return wrapper

    return decorator


class CacheContext:
    """
    Context manager for temporary cache bypass.

    Example:
        async with CacheContext(bypass=True):
            # This will skip cache and always fetch fresh data
            result = await cached_function()
    """

    def __init__(self, bypass: bool = False):
        self.bypass = bypass
        self._original_get = None

    async def __aenter__(self):
        if self.bypass:
            # Store original get method
            self._original_get = cache_manager.get
            # Replace with a method that always returns None (cache miss)
            cache_manager.get = self._bypass_get

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.bypass and self._original_get:
            # Restore original get method
            cache_manager.get = self._original_get

    @staticmethod
    async def _bypass_get(key: str) -> None:
        """Always return None to simulate cache miss."""
        return None


def conditional_cache(
    key_prefix: str,
    ttl: Optional[int] = None,
    condition: Optional[Callable[..., bool]] = None,
):
    """
    Decorator to conditionally cache function results based on arguments.

    Args:
        key_prefix: Prefix for cache keys
        ttl: Time-to-live in seconds
        condition: Function that returns True if result should be cached

    Example:
        @conditional_cache(
            key_prefix="user_data",
            ttl=300,
            condition=lambda user_id: user_id is not None
        )
        async def get_user_data(user_id: Optional[str]) -> dict:
            return {"id": user_id}
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check if we should cache
            should_cache = True
            if condition:
                should_cache = condition(*args, **kwargs)

            if not should_cache:
                # Don't use cache, just call the function
                return await func(*args, **kwargs)

            # Use caching
            cache_key = generate_cache_key(key_prefix, *args, **kwargs)

            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value

            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)

            await cache_manager.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


def cache_list_result(
    key_prefix: str,
    ttl: Optional[int] = None,
    max_items: Optional[int] = None,
):
    """
    Decorator to cache list results with optional size limiting.

    Args:
        key_prefix: Prefix for cache keys
        ttl: Time-to-live in seconds
        max_items: Maximum number of items to cache (None for unlimited)

    Example:
        @cache_list_result(key_prefix="top_products", ttl=300, max_items=10)
        async def get_top_products(limit: int = 10) -> list[Product]:
            return products[:limit]
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = generate_cache_key(key_prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value

            # Cache miss - call the function
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)

            # Limit the number of items if specified
            if max_items and isinstance(result, list) and len(result) > max_items:
                result = result[:max_items]

            # Store in cache
            await cache_manager.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator

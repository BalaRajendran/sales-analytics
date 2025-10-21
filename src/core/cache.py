"""Redis cache manager for high-performance caching.

This module provides a comprehensive caching layer using Redis with:
- Connection pooling
- Automatic serialization/deserialization
- TTL management
- Cache key patterns
- Hit/miss metrics
- Error handling with fallback
"""

import json
import logging
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from src.core.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager with async support.

    Provides a high-level interface for caching with automatic
    serialization, TTL management, and error handling.
    """

    def __init__(self):
        """Initialize cache manager with connection pool."""
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._hits = 0
        self._misses = 0

    async def connect(self) -> None:
        """Create Redis connection pool."""
        try:
            self._pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=False,  # We'll handle encoding/decoding
            )
            self._client = redis.Redis(connection_pool=self._pool)
            # Test connection
            await self._client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None

    async def disconnect(self) -> None:
        """Close Redis connection pool."""
        if self._client:
            await self._client.close()
            logger.info("Redis connection closed")

    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._client is not None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, cache miss")
            self._misses += 1
            return None

        try:
            value = await self._client.get(key)
            if value is None:
                self._misses += 1
                logger.debug(f"Cache miss: {key}")
                return None

            self._hits += 1
            logger.debug(f"Cache hit: {key}")
            # Deserialize JSON
            return json.loads(value)
        except json.JSONDecodeError:
            logger.error(f"Failed to deserialize cached value for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (None = no expiration)

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Redis not connected, skipping cache set")
            return False

        try:
            # Serialize to JSON
            serialized = json.dumps(value)

            if ttl:
                await self._client.setex(key, ttl, serialized)
            else:
                await self._client.set(key, serialized)

            logger.debug(f"Cache set: {key} (TTL: {ttl})")
            return True
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize value for key {key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            result = await self._client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Pattern to match (e.g., "analytics:product:*")

        Returns:
            Number of keys deleted
        """
        if not self.is_connected():
            return 0

        try:
            # Find matching keys
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                result = await self._client.delete(*keys)
                logger.info(f"Cache delete pattern: {pattern} ({result} keys)")
                return result
            return 0
        except Exception as e:
            logger.error(f"Error deleting cache pattern {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            result = await self._client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error checking cache key existence {key}: {e}")
            return False

    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for key.

        Args:
            key: Cache key

        Returns:
            Remaining TTL in seconds, None if key doesn't exist or has no expiration
        """
        if not self.is_connected():
            return None

        try:
            ttl = await self._client.ttl(key)
            if ttl == -2:  # Key doesn't exist
                return None
            if ttl == -1:  # Key exists but has no expiration
                return None
            return ttl
        except Exception as e:
            logger.error(f"Error getting TTL for key {key}: {e}")
            return None

    async def clear_all(self) -> bool:
        """Clear all keys in current database.

        WARNING: This will delete all keys in the current Redis database!

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False

        try:
            await self._client.flushdb()
            logger.warning("All cache keys cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache hit/miss stats
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0

        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "connected": self.is_connected(),
        }

    def reset_stats(self) -> None:
        """Reset cache statistics."""
        self._hits = 0
        self._misses = 0


# Global cache manager instance
cache_manager = CacheManager()


# Cache key patterns for consistent naming
class CacheKeys:
    """Cache key patterns for the application."""

    # Dashboard
    DASHBOARD_OVERVIEW = "analytics:dashboard:overview:{date_range}"
    REALTIME_METRICS = "analytics:realtime:metrics"

    # Products
    PRODUCT_INSIGHTS = "analytics:product:insights:{period}:{sort}"
    PRODUCT_PERFORMANCE = "analytics:product:{product_id}:{period}"
    TOP_PRODUCTS = "analytics:product:top:{limit}:{period}"
    CATEGORY_BREAKDOWN = "analytics:category:breakdown:{period}"

    # Customers
    CUSTOMER_SEGMENTS = "analytics:customer:segments"
    CUSTOMER_METRICS = "analytics:customer:{customer_id}:{period}"
    CUSTOMER_RETENTION = "analytics:customer:retention:{period}"
    TOP_CUSTOMERS = "analytics:customer:top:{limit}:{period}"

    # Sales
    SALES_TRENDS = "analytics:sales:trends:{metric}:{period}"
    SALES_OVERVIEW = "analytics:sales:overview:{date_range}"

    # Profitability
    PROFITABILITY_METRICS = "analytics:profitability:{period}"
    MARGIN_ANALYSIS = "analytics:margin:{group_by}:{period}"

    # Sales Reps
    SALES_REP_PERFORMANCE = "analytics:salesrep:{sales_rep_id}:{period}"
    TOP_SALES_REPS = "analytics:salesrep:top:{limit}:{period}"

    @staticmethod
    def format_key(pattern: str, **kwargs) -> str:
        """Format cache key with parameters.

        Args:
            pattern: Cache key pattern
            **kwargs: Parameters to substitute

        Returns:
            Formatted cache key

        Example:
            key = CacheKeys.format_key(
                CacheKeys.PRODUCT_PERFORMANCE,
                product_id="123",
                period="month"
            )
        """
        return pattern.format(**kwargs)


# Convenience functions
async def get_cached(key: str) -> Optional[Any]:
    """Get value from cache (convenience function).

    Args:
        key: Cache key

    Returns:
        Cached value if exists, None otherwise
    """
    return await cache_manager.get(key)


async def set_cached(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
) -> bool:
    """Set value in cache (convenience function).

    Args:
        key: Cache key
        value: Value to cache
        ttl: Time to live in seconds

    Returns:
        True if successful, False otherwise
    """
    return await cache_manager.set(key, value, ttl)


async def delete_cached(key: str) -> bool:
    """Delete key from cache (convenience function).

    Args:
        key: Cache key

    Returns:
        True if deleted, False otherwise
    """
    return await cache_manager.delete(key)


async def invalidate_pattern(pattern: str) -> int:
    """Invalidate all keys matching pattern (convenience function).

    Args:
        pattern: Pattern to match

    Returns:
        Number of keys deleted
    """
    return await cache_manager.delete_pattern(pattern)

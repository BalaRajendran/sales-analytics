"""
Tests for cache functionality.

Run with: pytest tests/test_cache.py -v
"""

import asyncio
from uuid import uuid4

import pytest

from src.core.cache import CacheManager, cache_manager
from src.core.cache_decorators import (
    cache_list_result,
    cache_result,
    cached,
    conditional_cache,
    invalidate_on_change,
)
from src.services.cache_invalidation import cache_invalidation_service


@pytest.fixture
async def setup_cache():
    """Setup cache manager for testing."""
    await cache_manager.connect()
    yield
    # Cleanup
    await cache_manager.clear_all()
    await cache_manager.disconnect()


@pytest.mark.asyncio
async def test_cache_basic_operations(setup_cache):
    """Test basic cache operations."""
    # Test set and get
    key = "test_key"
    value = {"name": "John", "age": 30}

    await cache_manager.set(key, value, ttl=60)
    result = await cache_manager.get(key)

    assert result == value

    # Test delete
    await cache_manager.delete(key)
    result = await cache_manager.get(key)
    assert result is None


@pytest.mark.asyncio
async def test_cache_ttl(setup_cache):
    """Test cache TTL functionality."""
    key = "test_ttl"
    value = "test_value"

    # Set with 2 second TTL
    await cache_manager.set(key, value, ttl=2)

    # Should exist immediately
    result = await cache_manager.get(key)
    assert result == value

    # Wait for expiration
    await asyncio.sleep(3)

    # Should be gone
    result = await cache_manager.get(key)
    assert result is None


@pytest.mark.asyncio
async def test_cache_pattern_deletion(setup_cache):
    """Test pattern-based cache deletion."""
    # Set multiple keys
    await cache_manager.set("product:123:daily", {"revenue": 1000})
    await cache_manager.set("product:123:weekly", {"revenue": 7000})
    await cache_manager.set("product:456:daily", {"revenue": 2000})
    await cache_manager.set("customer:789:daily", {"revenue": 5000})

    # Delete product:* pattern
    deleted = await cache_manager.delete_pattern("product:*")
    assert deleted == 3

    # Verify correct keys were deleted
    assert await cache_manager.get("product:123:daily") is None
    assert await cache_manager.get("product:123:weekly") is None
    assert await cache_manager.get("product:456:daily") is None

    # Customer key should still exist
    assert await cache_manager.get("customer:789:daily") is not None


@pytest.mark.asyncio
async def test_cache_decorator(setup_cache):
    """Test cache decorator functionality."""
    call_count = 0

    @cached(key_prefix="test_func", ttl=60)
    async def expensive_function(x: int, y: int) -> int:
        nonlocal call_count
        call_count += 1
        return x + y

    # First call - cache miss
    result1 = await expensive_function(5, 10)
    assert result1 == 15
    assert call_count == 1

    # Second call - cache hit
    result2 = await expensive_function(5, 10)
    assert result2 == 15
    assert call_count == 1  # Function not called again

    # Different args - cache miss
    result3 = await expensive_function(3, 7)
    assert result3 == 10
    assert call_count == 2


@pytest.mark.asyncio
async def test_cache_result_decorator(setup_cache):
    """Test cache_result decorator."""
    call_count = 0

    @cache_result(ttl=60)
    async def get_data(user_id: str) -> dict:
        nonlocal call_count
        call_count += 1
        return {"user_id": user_id, "name": "Test User"}

    # First call
    result1 = await get_data("user123")
    assert result1["user_id"] == "user123"
    assert call_count == 1

    # Second call - cached
    result2 = await get_data("user123")
    assert result2["user_id"] == "user123"
    assert call_count == 1


@pytest.mark.asyncio
async def test_invalidate_on_change_decorator(setup_cache):
    """Test invalidate_on_change decorator."""
    # Setup some cached data
    await cache_manager.set("product:123", {"name": "Product 123"})
    await cache_manager.set("product:456", {"name": "Product 456"})

    @invalidate_on_change(["product:*"])
    async def update_product(product_id: str) -> dict:
        return {"product_id": product_id, "updated": True}

    # Update product - should invalidate cache
    await update_product("123")

    # Verify cache was invalidated
    assert await cache_manager.get("product:123") is None
    assert await cache_manager.get("product:456") is None


@pytest.mark.asyncio
async def test_conditional_cache_decorator(setup_cache):
    """Test conditional_cache decorator."""
    call_count = 0

    @conditional_cache(
        key_prefix="user_data",
        ttl=60,
        condition=lambda user_id: user_id is not None and user_id != "skip",
    )
    async def get_user(user_id: str) -> dict:
        nonlocal call_count
        call_count += 1
        return {"user_id": user_id}

    # Normal user - should cache
    await get_user("user123")
    await get_user("user123")
    assert call_count == 1  # Cached

    # Skip user - should not cache
    await get_user("skip")
    await get_user("skip")
    assert call_count == 3  # Called twice (not cached)


@pytest.mark.asyncio
async def test_cache_list_result_decorator(setup_cache):
    """Test cache_list_result decorator."""
    call_count = 0

    @cache_list_result(key_prefix="products", ttl=60, max_items=5)
    async def get_products(limit: int = 10) -> list[dict]:
        nonlocal call_count
        call_count += 1
        return [{"id": i, "name": f"Product {i}"} for i in range(limit)]

    # Get 10 products, but only 5 will be cached
    result1 = await get_products(10)
    assert len(result1) == 5  # Limited by max_items
    assert call_count == 1

    # Second call - cached
    result2 = await get_products(10)
    assert len(result2) == 5
    assert call_count == 1


@pytest.mark.asyncio
async def test_cache_invalidation_service(setup_cache):
    """Test cache invalidation service."""
    # Setup test data
    await cache_manager.set("analytics:dashboard:overview:7d", {"revenue": 10000})
    await cache_manager.set("analytics:dashboard:overview:30d", {"revenue": 40000})
    await cache_manager.set("analytics:product:123:daily", {"sales": 100})

    # Test dashboard invalidation
    deleted = await cache_invalidation_service.invalidate_dashboard_cache()
    assert deleted == 2

    # Verify dashboard caches are gone
    assert await cache_manager.get("analytics:dashboard:overview:7d") is None
    assert await cache_manager.get("analytics:dashboard:overview:30d") is None

    # Product cache should still exist
    assert await cache_manager.get("analytics:product:123:daily") is not None


@pytest.mark.asyncio
async def test_cache_invalidation_on_order_created(setup_cache):
    """Test cache invalidation when order is created."""
    # Setup test data
    await cache_manager.set("analytics:dashboard:overview:7d", {"revenue": 10000})
    await cache_manager.set("analytics:customer:123:7d", {"orders": 5})
    await cache_manager.set("analytics:revenue_trends:7d", {"trend": "up"})
    await cache_manager.set("analytics:realtime_metrics", {"active": 100})

    # Simulate order creation
    order_id = uuid4()
    customer_id = uuid4()
    await cache_invalidation_service.on_order_created(order_id, customer_id)

    # All related caches should be invalidated
    assert await cache_manager.get("analytics:dashboard:overview:7d") is None
    assert await cache_manager.get("analytics:customer:123:7d") is None
    assert await cache_manager.get("analytics:revenue_trends:7d") is None
    assert await cache_manager.get("analytics:realtime_metrics") is None


@pytest.mark.asyncio
async def test_cache_stats(setup_cache):
    """Test cache hit/miss statistics."""
    # Reset stats
    stats = await cache_manager.get_stats()
    initial_hits = stats["hits"]
    initial_misses = stats["misses"]

    # Generate some cache activity
    await cache_manager.set("test_key", "test_value")

    # Cache hit
    await cache_manager.get("test_key")

    # Cache miss
    await cache_manager.get("nonexistent_key")

    # Check stats
    stats = await cache_manager.get_stats()
    assert stats["hits"] == initial_hits + 1
    assert stats["misses"] == initial_misses + 1


@pytest.mark.asyncio
async def test_cache_exists(setup_cache):
    """Test cache exists functionality."""
    key = "test_exists"
    value = {"data": "test"}

    # Key doesn't exist
    assert await cache_manager.exists(key) is False

    # Set key
    await cache_manager.set(key, value)

    # Key exists
    assert await cache_manager.exists(key) is True

    # Delete key
    await cache_manager.delete(key)

    # Key doesn't exist again
    assert await cache_manager.exists(key) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Examples of using the cache system in the Sales Dashboard API.

This file demonstrates various caching patterns and best practices.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import CacheKeys, cache_manager
from src.core.cache_decorators import (
    cache_list_result,
    cache_result,
    cached,
    invalidate_on_change,
)
from src.core.config import settings
from src.models.product import Product
from src.services.cache_invalidation import cache_invalidation_service


# Example 1: Manual cache usage
async def get_dashboard_metrics_manual(date_range: str, db: AsyncSession) -> dict:
    """
    Example of manual cache usage for dashboard metrics.

    This approach gives you full control over cache keys and TTL.
    """
    # Build cache key
    cache_key = CacheKeys.DASHBOARD_OVERVIEW.format(date_range=date_range)

    # Try to get from cache
    cached_data = await cache_manager.get(cache_key)
    if cached_data:
        return cached_data

    # Cache miss - fetch from database
    # (Simulated complex query)
    metrics = {
        "total_revenue": 125000.50,
        "total_orders": 450,
        "avg_order_value": 277.78,
        "top_products": [],
        "cached_at": datetime.utcnow().isoformat(),
    }

    # Store in cache with appropriate TTL
    await cache_manager.set(cache_key, metrics, ttl=settings.CACHE_TTL_DASHBOARD)

    return metrics


# Example 2: Using @cached decorator
@cached(key_prefix="product_performance", ttl=settings.CACHE_TTL_PRODUCTS)
async def get_product_performance(product_id: UUID, period: str, db: AsyncSession) -> dict:
    """
    Example using @cached decorator for product performance metrics.

    The decorator automatically handles cache key generation and storage.
    """
    # Fetch product data from database
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        return {"error": "Product not found"}

    # Calculate metrics (simulated)
    return {
        "product_id": str(product_id),
        "product_name": product.name,
        "period": period,
        "total_revenue": 15000.00,
        "units_sold": 125,
        "profit_margin": float(product.profit_margin_percentage),
        "cached_at": datetime.utcnow().isoformat(),
    }


# Example 3: Using @cache_result with automatic key generation
@cache_result(ttl=settings.CACHE_TTL_CUSTOMERS)
async def get_customer_lifetime_value(customer_id: UUID, db: AsyncSession) -> Decimal:
    """
    Example using @cache_result for simple value caching.

    Cache key is automatically generated from function name and arguments.
    """
    # Simulate complex calculation
    # In reality, this would query orders and calculate total value
    return Decimal("5432.10")


# Example 4: Caching list results with size limiting
@cache_list_result(key_prefix="top_products", ttl=settings.CACHE_TTL_PRODUCTS, max_items=10)
async def get_top_products(category_id: Optional[UUID], limit: int, db: AsyncSession) -> list[dict]:
    """
    Example of caching list results with size limiting.

    Even if limit=100, only 10 items will be cached to save memory.
    """
    # Simulate database query for top products
    products = [
        {
            "id": str(uuid4()),
            "name": f"Product {i}",
            "revenue": 10000 - (i * 100),
            "units_sold": 500 - (i * 10),
        }
        for i in range(limit)
    ]

    return products


# Example 5: Cache invalidation on data changes
@invalidate_on_change(["product:*", "analytics:dashboard:*", "analytics:category:*"])
async def update_product_price(product_id: UUID, new_price: Decimal, db: AsyncSession) -> Product:
    """
    Example of automatic cache invalidation after data mutation.

    When product price changes, all related caches are invalidated.
    """
    # Update product in database
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if product:
        product.selling_price = new_price
        await db.commit()
        await db.refresh(product)

    return product


# Example 6: Manual cache invalidation in service layer
class ProductService:
    """Example service with manual cache invalidation."""

    @staticmethod
    async def create_product(product_data: dict, db: AsyncSession) -> Product:
        """Create a new product and invalidate related caches."""
        # Create product
        product = Product(**product_data)
        db.add(product)
        await db.commit()
        await db.refresh(product)

        # Invalidate related caches
        await cache_invalidation_service.invalidate_product_cache()
        await cache_invalidation_service.invalidate_category_cache(product.category_id)
        await cache_invalidation_service.invalidate_dashboard_cache()

        return product

    @staticmethod
    async def update_product(product_id: UUID, product_data: dict, db: AsyncSession) -> Product:
        """Update a product and invalidate specific caches."""
        # Update product
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()

        if not product:
            raise ValueError("Product not found")

        for key, value in product_data.items():
            setattr(product, key, value)

        await db.commit()
        await db.refresh(product)

        # Invalidate caches for this specific product and its category
        await cache_invalidation_service.on_product_updated(product_id, product.category_id)

        return product


# Example 7: Cache warming strategy
async def warm_dashboard_cache(db: AsyncSession) -> None:
    """
    Pre-populate cache with commonly accessed data.

    This is typically run after materialized view refresh or during deployment.
    """
    date_ranges = ["7d", "30d", "90d"]

    for date_range in date_ranges:
        # Fetch and cache dashboard metrics
        metrics = await get_dashboard_metrics_manual(date_range, db)
        print(f"Warmed cache for date range: {date_range}")


# Example 8: Cache monitoring and health check
async def check_cache_health() -> dict:
    """
    Check cache health and performance metrics.

    Useful for monitoring and alerting.
    """
    try:
        # Test cache connectivity
        test_key = "health_check_test"
        await cache_manager.set(test_key, "ok", ttl=10)
        test_value = await cache_manager.get(test_key)

        if test_value != "ok":
            return {"status": "unhealthy", "reason": "Cache read/write failed"}

        # Get cache statistics
        stats = await cache_manager.get_stats()

        # Calculate hit rate
        total_requests = stats["hits"] + stats["misses"]
        hit_rate = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "status": "healthy",
            "stats": stats,
            "hit_rate_percentage": round(hit_rate, 2),
            "target_hit_rate": 80.0,  # Target from architecture
            "meeting_target": hit_rate >= 80.0,
        }

    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}


# Example 9: Complex cache key patterns
class AnalyticsService:
    """Example service with complex cache key patterns."""

    @staticmethod
    async def get_revenue_by_region(region: str, period: str, db: AsyncSession) -> dict:
        """Revenue analytics by region with custom cache key."""
        cache_key = f"analytics:revenue:region:{region}:{period}"

        # Try cache first
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            return cached_data

        # Fetch from database (simulated)
        revenue_data = {
            "region": region,
            "period": period,
            "total_revenue": 50000.00,
            "orders": 200,
            "cached_at": datetime.utcnow().isoformat(),
        }

        # Cache with appropriate TTL based on period
        ttl = settings.CACHE_TTL_DASHBOARD if period == "today" else settings.CACHE_TTL_TRENDS
        await cache_manager.set(cache_key, revenue_data, ttl=ttl)

        return revenue_data


# Example 10: Batch cache operations
async def get_multiple_products(product_ids: list[UUID], db: AsyncSession) -> list[dict]:
    """
    Efficiently fetch multiple products using cache.

    This pattern checks cache first, then fetches only missing items from DB.
    """
    results = []
    missing_ids = []

    # Check cache for each product
    for product_id in product_ids:
        cache_key = f"product:{product_id}:details"
        cached_product = await cache_manager.get(cache_key)

        if cached_product:
            results.append(cached_product)
        else:
            missing_ids.append(product_id)

    # Fetch missing products from database
    if missing_ids:
        stmt = select(Product).where(Product.id.in_(missing_ids))
        result = await db.execute(stmt)
        products = result.scalars().all()

        for product in products:
            product_data = {
                "id": str(product.id),
                "name": product.name,
                "price": float(product.selling_price),
            }

            # Cache each product
            cache_key = f"product:{product.id}:details"
            await cache_manager.set(cache_key, product_data, ttl=settings.CACHE_TTL_PRODUCTS)

            results.append(product_data)

    return results


# Example 11: Cache with fallback
async def get_realtime_metrics_with_fallback(db: AsyncSession) -> dict:
    """
    Get realtime metrics with graceful fallback if cache fails.

    This pattern ensures the application continues working even if Redis is down.
    """
    cache_key = CacheKeys.REALTIME_METRICS

    try:
        # Try to get from cache
        cached_data = await cache_manager.get(cache_key)
        if cached_data:
            return cached_data
    except Exception as e:
        print(f"Cache error: {e}, falling back to database")

    # Fallback to database
    metrics = {
        "active_users": 150,
        "pending_orders": 23,
        "revenue_today": 8500.00,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        # Try to cache for next request
        await cache_manager.set(cache_key, metrics, ttl=settings.CACHE_TTL_REALTIME)
    except Exception:
        # If caching fails, just return the data
        pass

    return metrics


# Best Practices Summary:
"""
1. Use appropriate TTL based on data volatility:
   - Realtime metrics: 30s
   - Dashboard overview: 60s
   - Product data: 300s (5 min)
   - Customer data: 600s (10 min)
   - Trend analysis: 180s (3 min)

2. Always invalidate cache when data changes:
   - Use @invalidate_on_change decorator
   - Or call cache_invalidation_service methods

3. Use decorators for simple cases:
   - @cached for custom keys
   - @cache_result for automatic keys
   - @cache_list_result for list data

4. Monitor cache performance:
   - Target hit rate: > 80%
   - Track hits/misses
   - Alert on low hit rates

5. Implement graceful fallback:
   - Application should work if Redis is down
   - Try-except blocks around cache operations
   - Fall back to database queries

6. Use cache warming after MV refresh:
   - Pre-populate cache with common queries
   - Reduces cold start impact

7. Pattern-based invalidation:
   - Use wildcards for bulk invalidation
   - Example: "product:*" invalidates all product caches
"""

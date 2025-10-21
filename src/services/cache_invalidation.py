"""
Cache invalidation service.

Handles automatic cache invalidation based on data changes.
"""

import logging
from typing import Any, Optional
from uuid import UUID

from src.core.cache import cache_manager, CacheKeys

logger = logging.getLogger(__name__)


class CacheInvalidationService:
    """Service for invalidating cache when data changes."""

    @staticmethod
    async def invalidate_dashboard_cache() -> int:
        """
        Invalidate all dashboard overview caches.

        Returns:
            Number of keys deleted
        """
        pattern = CacheKeys.DASHBOARD_OVERVIEW.replace("{date_range}", "*")
        deleted = await cache_manager.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} dashboard cache keys")
        return deleted

    @staticmethod
    async def invalidate_product_cache(product_id: Optional[UUID] = None) -> int:
        """
        Invalidate product-related caches.

        Args:
            product_id: Specific product to invalidate, or None for all products

        Returns:
            Number of keys deleted
        """
        if product_id:
            pattern = CacheKeys.PRODUCT_PERFORMANCE.replace(
                "{product_id}", str(product_id)
            ).replace("{period}", "*")
        else:
            pattern = CacheKeys.PRODUCT_PERFORMANCE.replace("{product_id}", "*").replace(
                "{period}", "*"
            )

        deleted = await cache_manager.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} product cache keys")
        return deleted

    @staticmethod
    async def invalidate_customer_cache(customer_id: Optional[UUID] = None) -> int:
        """
        Invalidate customer-related caches.

        Args:
            customer_id: Specific customer to invalidate, or None for all customers

        Returns:
            Number of keys deleted
        """
        if customer_id:
            pattern = CacheKeys.CUSTOMER_METRICS.replace(
                "{customer_id}", str(customer_id)
            ).replace("{period}", "*")
        else:
            pattern = CacheKeys.CUSTOMER_METRICS.replace("{customer_id}", "*").replace(
                "{period}", "*"
            )

        deleted = await cache_manager.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} customer cache keys")
        return deleted

    @staticmethod
    async def invalidate_sales_rep_cache(sales_rep_id: Optional[UUID] = None) -> int:
        """
        Invalidate sales representative-related caches.

        Args:
            sales_rep_id: Specific sales rep to invalidate, or None for all

        Returns:
            Number of keys deleted
        """
        if sales_rep_id:
            pattern = CacheKeys.SALES_REP_PERFORMANCE.replace(
                "{sales_rep_id}", str(sales_rep_id)
            ).replace("{period}", "*")
        else:
            pattern = CacheKeys.SALES_REP_PERFORMANCE.replace(
                "{sales_rep_id}", "*"
            ).replace("{period}", "*")

        deleted = await cache_manager.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} sales rep cache keys")
        return deleted

    @staticmethod
    async def invalidate_category_cache(category_id: Optional[UUID] = None) -> int:
        """
        Invalidate category-related caches.

        Args:
            category_id: Specific category to invalidate, or None for all

        Returns:
            Number of keys deleted
        """
        if category_id:
            pattern = CacheKeys.CATEGORY_PERFORMANCE.replace(
                "{category_id}", str(category_id)
            ).replace("{period}", "*")
        else:
            pattern = CacheKeys.CATEGORY_PERFORMANCE.replace(
                "{category_id}", "*"
            ).replace("{period}", "*")

        deleted = await cache_manager.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} category cache keys")
        return deleted

    @staticmethod
    async def invalidate_trends_cache() -> int:
        """
        Invalidate all trend analysis caches.

        Returns:
            Number of keys deleted
        """
        patterns = [
            CacheKeys.REVENUE_TRENDS.replace("{period}", "*"),
            CacheKeys.PROFIT_TRENDS.replace("{period}", "*"),
            CacheKeys.ORDER_TRENDS.replace("{period}", "*"),
        ]

        total_deleted = 0
        for pattern in patterns:
            deleted = await cache_manager.delete_pattern(pattern)
            total_deleted += deleted

        logger.info(f"Invalidated {total_deleted} trend cache keys")
        return total_deleted

    @staticmethod
    async def invalidate_realtime_cache() -> int:
        """
        Invalidate real-time metrics cache.

        Returns:
            Number of keys deleted
        """
        pattern = CacheKeys.REALTIME_METRICS
        deleted = await cache_manager.delete_pattern(pattern)
        logger.info(f"Invalidated {deleted} realtime cache keys")
        return deleted

    @staticmethod
    async def on_order_created(order_id: UUID, customer_id: UUID) -> None:
        """
        Handle cache invalidation when a new order is created.

        Args:
            order_id: ID of the created order
            customer_id: ID of the customer who placed the order
        """
        logger.info(f"Order {order_id} created, invalidating related caches")

        # Invalidate dashboard (affects total revenue, orders count)
        await CacheInvalidationService.invalidate_dashboard_cache()

        # Invalidate customer cache (affects customer metrics)
        await CacheInvalidationService.invalidate_customer_cache(customer_id)

        # Invalidate trends (affects revenue and order trends)
        await CacheInvalidationService.invalidate_trends_cache()

        # Invalidate realtime metrics
        await CacheInvalidationService.invalidate_realtime_cache()

    @staticmethod
    async def on_order_updated(
        order_id: UUID, customer_id: UUID, status_changed: bool = False
    ) -> None:
        """
        Handle cache invalidation when an order is updated.

        Args:
            order_id: ID of the updated order
            customer_id: ID of the customer
            status_changed: Whether order status changed (e.g., pending -> completed)
        """
        logger.info(f"Order {order_id} updated, invalidating related caches")

        if status_changed:
            # Status changes affect more metrics
            await CacheInvalidationService.invalidate_dashboard_cache()
            await CacheInvalidationService.invalidate_customer_cache(customer_id)
            await CacheInvalidationService.invalidate_trends_cache()

        # Always invalidate realtime metrics
        await CacheInvalidationService.invalidate_realtime_cache()

    @staticmethod
    async def on_product_updated(product_id: UUID, category_id: UUID) -> None:
        """
        Handle cache invalidation when a product is updated.

        Args:
            product_id: ID of the updated product
            category_id: ID of the product's category
        """
        logger.info(f"Product {product_id} updated, invalidating related caches")

        # Invalidate product cache
        await CacheInvalidationService.invalidate_product_cache(product_id)

        # Invalidate category cache (affects category metrics)
        await CacheInvalidationService.invalidate_category_cache(category_id)

        # Invalidate dashboard (might affect top products)
        await CacheInvalidationService.invalidate_dashboard_cache()

    @staticmethod
    async def on_customer_updated(customer_id: UUID) -> None:
        """
        Handle cache invalidation when a customer is updated.

        Args:
            customer_id: ID of the updated customer
        """
        logger.info(f"Customer {customer_id} updated, invalidating related caches")

        # Invalidate customer cache
        await CacheInvalidationService.invalidate_customer_cache(customer_id)

        # Invalidate dashboard (might affect customer segments)
        await CacheInvalidationService.invalidate_dashboard_cache()

    @staticmethod
    async def on_sales_rep_updated(sales_rep_id: UUID) -> None:
        """
        Handle cache invalidation when a sales representative is updated.

        Args:
            sales_rep_id: ID of the updated sales rep
        """
        logger.info(f"Sales rep {sales_rep_id} updated, invalidating related caches")

        # Invalidate sales rep cache
        await CacheInvalidationService.invalidate_sales_rep_cache(sales_rep_id)

        # Invalidate dashboard (might affect sales rep performance)
        await CacheInvalidationService.invalidate_dashboard_cache()

    @staticmethod
    async def on_materialized_view_refreshed(view_name: str) -> None:
        """
        Handle cache invalidation when a materialized view is refreshed.

        This should be called after scheduled MV refreshes to invalidate
        dependent caches.

        Args:
            view_name: Name of the refreshed materialized view
        """
        logger.info(f"Materialized view {view_name} refreshed, invalidating all caches")

        # Materialized view refreshes affect all derived metrics
        await CacheInvalidationService.invalidate_dashboard_cache()
        await CacheInvalidationService.invalidate_product_cache()
        await CacheInvalidationService.invalidate_customer_cache()
        await CacheInvalidationService.invalidate_sales_rep_cache()
        await CacheInvalidationService.invalidate_category_cache()
        await CacheInvalidationService.invalidate_trends_cache()

    @staticmethod
    async def clear_all_cache() -> bool:
        """
        Clear all application caches.

        Use with caution - this clears everything!

        Returns:
            True if successful
        """
        logger.warning("Clearing ALL application caches")
        return await cache_manager.clear_all()


# Singleton instance
cache_invalidation_service = CacheInvalidationService()

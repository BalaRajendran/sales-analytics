"""
Analytics background tasks.

Tasks for refreshing materialized views, cache warming, and report generation.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import text

from src.celery_app import celery_app
from src.core.cache import CacheKeys, cache_manager
from src.core.database import AsyncSessionLocal
from src.services.analytics_service import analytics_service
from src.services.cache_invalidation import cache_invalidation_service

logger = logging.getLogger(__name__)


@celery_app.task(name="src.tasks.analytics_tasks.refresh_realtime_materialized_views")
def refresh_realtime_materialized_views() -> dict[str, Any]:
    """
    Refresh real-time materialized views.

    Runs every 5 minutes to keep real-time metrics up to date.
    Refreshes: hourly_metrics, realtime dashboard views.
    """
    import asyncio

    async def _refresh():
        async with AsyncSessionLocal() as db:
            try:
                # Refresh hourly metrics materialized view
                await db.execute(text("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hourly_metrics"))
                await db.commit()

                logger.info("✓ Refreshed real-time materialized views")

                # Invalidate related caches
                await cache_invalidation_service.on_materialized_view_refreshed(
                    "mv_hourly_metrics"
                )

                return {
                    "status": "success",
                    "views_refreshed": ["mv_hourly_metrics"],
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to refresh real-time MVs: {e}")
                await db.rollback()
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_refresh())


@celery_app.task(name="src.tasks.analytics_tasks.refresh_daily_materialized_views")
def refresh_daily_materialized_views() -> dict[str, Any]:
    """
    Refresh daily aggregated materialized views.

    Runs every hour to update daily aggregations.
    Refreshes: daily_sales, product_performance, customer_segments, etc.
    """
    import asyncio

    async def _refresh():
        async with AsyncSessionLocal() as db:
            try:
                views_to_refresh = [
                    "mv_daily_sales",
                    "mv_product_performance",
                    "mv_customer_segments",
                    "mv_category_performance",
                    "mv_sales_rep_performance",
                ]

                for view_name in views_to_refresh:
                    try:
                        await db.execute(
                            text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name}")
                        )
                        logger.info(f"✓ Refreshed {view_name}")
                    except Exception as e:
                        logger.error(f"Failed to refresh {view_name}: {e}")

                await db.commit()

                # Invalidate all analytics caches
                await cache_invalidation_service.on_materialized_view_refreshed("all_daily_views")

                logger.info(f"✓ Refreshed {len(views_to_refresh)} daily materialized views")

                return {
                    "status": "success",
                    "views_refreshed": views_to_refresh,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to refresh daily MVs: {e}")
                await db.rollback()
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_refresh())


@celery_app.task(name="src.tasks.analytics_tasks.warm_dashboard_cache")
def warm_dashboard_cache() -> dict[str, Any]:
    """
    Pre-populate cache with common dashboard queries.

    Runs every 2 minutes to ensure fast dashboard loads.
    Warms cache for: 7d, 30d, 90d date ranges.
    """
    import asyncio

    async def _warm_cache():
        async with AsyncSessionLocal() as db:
            try:
                date_ranges = [
                    ("7d", timedelta(days=7)),
                    ("30d", timedelta(days=30)),
                    ("90d", timedelta(days=90)),
                ]

                warmed_count = 0
                end_date = datetime.utcnow()

                for range_key, delta in date_ranges:
                    start_date = end_date - delta

                    # Warm revenue metrics
                    await analytics_service.get_revenue_metrics(db, start_date, end_date)
                    warmed_count += 1

                    # Warm order metrics
                    await analytics_service.get_order_metrics(db, start_date, end_date)
                    warmed_count += 1

                    # Warm top products
                    await analytics_service.get_top_products(db, start_date, end_date, limit=5)
                    warmed_count += 1

                    # Warm trends
                    await analytics_service.get_revenue_trend(db, start_date, end_date)
                    warmed_count += 1

                logger.info(f"✓ Warmed {warmed_count} cache entries for dashboard")

                return {
                    "status": "success",
                    "cache_entries_warmed": warmed_count,
                    "date_ranges": [r[0] for r in date_ranges],
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to warm dashboard cache: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_warm_cache())


@celery_app.task(name="src.tasks.analytics_tasks.generate_monthly_report")
def generate_monthly_report() -> dict[str, Any]:
    """
    Generate comprehensive monthly report.

    Runs on the 1st of each month at 6 AM.
    Generates report for previous month.
    """
    import asyncio

    async def _generate_report():
        async with AsyncSessionLocal() as db:
            try:
                # Calculate previous month date range
                today = datetime.utcnow()
                first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = first_of_this_month - timedelta(seconds=1)
                start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

                month_name = start_date.strftime("%B %Y")

                # Gather metrics
                revenue_metrics = await analytics_service.get_revenue_metrics(
                    db, start_date, end_date
                )
                order_metrics = await analytics_service.get_order_metrics(
                    db, start_date, end_date
                )
                top_products = await analytics_service.get_top_products(
                    db, start_date, end_date, limit=10
                )
                top_customers = await analytics_service.get_top_customers(
                    db, start_date, end_date, limit=10
                )
                top_sales_reps = await analytics_service.get_top_sales_reps(
                    db, start_date, end_date, limit=10
                )
                regional_performance = await analytics_service.get_regional_performance(
                    db, start_date, end_date
                )

                report = {
                    "report_type": "monthly",
                    "period": month_name,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "generated_at": datetime.utcnow().isoformat(),
                    "metrics": {
                        "revenue": revenue_metrics,
                        "orders": order_metrics,
                        "top_products": top_products[:5],
                        "top_customers": top_customers[:5],
                        "top_sales_reps": top_sales_reps[:5],
                        "regional_performance": regional_performance,
                    },
                }

                logger.info(f"✓ Generated monthly report for {month_name}")

                # Store report in cache for retrieval
                cache_key = f"report:monthly:{start_date.strftime('%Y-%m')}"
                await cache_manager.set(cache_key, report, ttl=86400 * 90)  # 90 days

                return {
                    "status": "success",
                    "report_period": month_name,
                    "cache_key": cache_key,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to generate monthly report: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_generate_report())


@celery_app.task(name="src.tasks.analytics_tasks.calculate_product_rankings")
def calculate_product_rankings() -> dict[str, Any]:
    """
    Calculate and cache product rankings.

    Updates product performance rankings based on recent sales.
    """
    import asyncio

    async def _calculate_rankings():
        async with AsyncSessionLocal() as db:
            try:
                end_date = datetime.utcnow()
                periods = [
                    ("7d", timedelta(days=7)),
                    ("30d", timedelta(days=30)),
                    ("90d", timedelta(days=90)),
                ]

                rankings_updated = 0

                for period_key, delta in periods:
                    start_date = end_date - delta

                    # Get top products
                    top_products = await analytics_service.get_top_products(
                        db, start_date, end_date, limit=50
                    )

                    # Cache rankings
                    cache_key = f"rankings:products:{period_key}"
                    await cache_manager.set(cache_key, top_products, ttl=3600)  # 1 hour
                    rankings_updated += 1

                logger.info(f"✓ Updated product rankings for {len(periods)} periods")

                return {
                    "status": "success",
                    "periods_updated": rankings_updated,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to calculate product rankings: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_calculate_rankings())


@celery_app.task(name="src.tasks.analytics_tasks.refresh_all_materialized_views")
def refresh_all_materialized_views() -> dict[str, Any]:
    """
    Refresh all materialized views.

    Manual task for full refresh. Can be triggered on-demand.
    """
    import asyncio

    async def _refresh_all():
        async with AsyncSessionLocal() as db:
            try:
                # Call the stored procedure to refresh all MVs
                await db.execute(text("SELECT refresh_all_analytics_mv()"))
                await db.commit()

                logger.info("✓ Refreshed all materialized views")

                # Clear all analytics caches
                await cache_invalidation_service.clear_all_cache()

                return {
                    "status": "success",
                    "message": "All materialized views refreshed",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to refresh all MVs: {e}")
                await db.rollback()
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_refresh_all())


@celery_app.task(name="src.tasks.analytics_tasks.export_analytics_data")
def export_analytics_data(
    start_date: str, end_date: str, export_format: str = "json"
) -> dict[str, Any]:
    """
    Export analytics data for a date range.

    Args:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        export_format: Format (json, csv)

    Returns:
        Export result with data or file path
    """
    import asyncio

    async def _export():
        async with AsyncSessionLocal() as db:
            try:
                start = datetime.fromisoformat(start_date)
                end = datetime.fromisoformat(end_date)

                # Gather all analytics data
                data = {
                    "export_date": datetime.utcnow().isoformat(),
                    "period": {"start": start_date, "end": end_date},
                    "revenue_metrics": await analytics_service.get_revenue_metrics(db, start, end),
                    "order_metrics": await analytics_service.get_order_metrics(db, start, end),
                    "top_products": await analytics_service.get_top_products(
                        db, start, end, limit=100
                    ),
                    "top_customers": await analytics_service.get_top_customers(
                        db, start, end, limit=100
                    ),
                    "regional_performance": await analytics_service.get_regional_performance(
                        db, start, end
                    ),
                }

                logger.info(f"✓ Exported analytics data for {start_date} to {end_date}")

                return {
                    "status": "success",
                    "format": export_format,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to export analytics data: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_export())

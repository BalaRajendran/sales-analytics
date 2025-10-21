"""
Maintenance background tasks.

Tasks for database maintenance, data cleanup, and system health.
"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import text

from src.celery_app import celery_app
from src.core.database import AsyncSessionLocal
from src.services.customer_service import customer_service

logger = logging.getLogger(__name__)


@celery_app.task(name="src.tasks.maintenance_tasks.update_customer_segments")
def update_customer_segments() -> dict[str, Any]:
    """
    Update all customer segments based on behavior.

    Runs daily at 2 AM.
    Assigns segments: Premium, Regular, New, At-Risk, Churned.
    """
    import asyncio

    async def _update_segments():
        async with AsyncSessionLocal() as db:
            try:
                # Bulk assign segments to all customers
                updated_count = await customer_service.bulk_assign_segments(db)

                logger.info(f"✓ Updated segments for {updated_count} customers")

                return {
                    "status": "success",
                    "customers_updated": updated_count,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to update customer segments: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_update_segments())


@celery_app.task(name="src.tasks.maintenance_tasks.update_customer_lifetime_values")
def update_customer_lifetime_values() -> dict[str, Any]:
    """
    Recalculate lifetime values for all customers.

    Runs daily at 3 AM.
    Ensures LTV is accurate based on completed orders.
    """
    import asyncio

    async def _update_ltv():
        async with AsyncSessionLocal() as db:
            try:
                from sqlalchemy import select
                from src.models.customer import Customer

                # Get all customers
                stmt = select(Customer)
                result = await db.execute(stmt)
                customers = result.scalars().all()

                updated_count = 0
                for customer in customers:
                    await customer_service.update_lifetime_value(db, customer.id)
                    updated_count += 1

                logger.info(f"✓ Updated LTV for {updated_count} customers")

                return {
                    "status": "success",
                    "customers_updated": updated_count,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to update customer LTV: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_update_ltv())


@celery_app.task(name="src.tasks.maintenance_tasks.clean_old_order_partitions")
def clean_old_order_partitions() -> dict[str, Any]:
    """
    Drop old order partitions to save space.

    Runs weekly on Sunday at 4 AM.
    Drops partitions older than 24 months.
    """
    import asyncio

    async def _clean_partitions():
        async with AsyncSessionLocal() as db:
            try:
                # Call the stored procedure
                result = await db.execute(
                    text("SELECT drop_old_order_partitions(24)")  # 24 months
                )
                dropped_count = result.scalar()
                await db.commit()

                logger.info(f"✓ Dropped {dropped_count} old order partitions")

                return {
                    "status": "success",
                    "partitions_dropped": dropped_count,
                    "retention_months": 24,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to clean old partitions: {e}")
                await db.rollback()
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_clean_partitions())


@celery_app.task(name="src.tasks.maintenance_tasks.create_next_month_partition")
def create_next_month_partition() -> dict[str, Any]:
    """
    Create order partition for next month.

    Runs on 25th of each month to prepare for next month.
    """
    import asyncio

    async def _create_partition():
        async with AsyncSessionLocal() as db:
            try:
                # Call the stored procedure
                result = await db.execute(text("SELECT create_next_month_order_partition()"))
                partition_name = result.scalar()
                await db.commit()

                logger.info(f"✓ Created partition: {partition_name}")

                return {
                    "status": "success",
                    "partition_created": partition_name,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to create next month partition: {e}")
                await db.rollback()
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_create_partition())


@celery_app.task(name="src.tasks.maintenance_tasks.vacuum_analyze_tables")
def vacuum_analyze_tables() -> dict[str, Any]:
    """
    Run VACUUM ANALYZE on main tables.

    Improves query performance and reclaims space.
    Runs weekly.
    """
    import asyncio

    async def _vacuum():
        async with AsyncSessionLocal() as db:
            try:
                tables = [
                    "orders",
                    "order_items",
                    "products",
                    "customers",
                    "sales_representatives",
                ]

                for table in tables:
                    await db.execute(text(f"VACUUM ANALYZE {table}"))
                    logger.info(f"✓ Vacuumed {table}")

                await db.commit()

                logger.info(f"✓ Vacuumed {len(tables)} tables")

                return {
                    "status": "success",
                    "tables_vacuumed": tables,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to vacuum tables: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_vacuum())


@celery_app.task(name="src.tasks.maintenance_tasks.update_aggregation_tables")
def update_aggregation_tables() -> dict[str, Any]:
    """
    Update aggregation tables with latest data.

    Runs every 30 minutes.
    Updates: agg_hourly_metrics, agg_category_performance.
    """
    import asyncio

    async def _update_agg_tables():
        async with AsyncSessionLocal() as db:
            try:
                # Truncate and rebuild aggregation tables
                await db.execute(text("TRUNCATE agg_hourly_metrics"))
                await db.execute(
                    text(
                        """
                    INSERT INTO agg_hourly_metrics (hour, revenue, orders_count, avg_order_value)
                    SELECT
                        EXTRACT(HOUR FROM order_date) as hour,
                        SUM(total_amount) as revenue,
                        COUNT(*) as orders_count,
                        AVG(total_amount) as avg_order_value
                    FROM orders
                    WHERE order_date >= CURRENT_DATE - INTERVAL '7 days'
                      AND status = 'completed'
                    GROUP BY EXTRACT(HOUR FROM order_date)
                """
                    )
                )

                await db.execute(text("TRUNCATE agg_category_performance"))
                await db.execute(
                    text(
                        """
                    INSERT INTO agg_category_performance
                        (category_id, category_name, products_count, total_revenue, total_profit)
                    SELECT
                        c.id,
                        c.name,
                        COUNT(DISTINCT p.id),
                        COALESCE(SUM(oi.total_price), 0),
                        COALESCE(SUM(oi.quantity * (oi.unit_price - p.cost_price)), 0)
                    FROM categories c
                    LEFT JOIN products p ON c.id = p.category_id
                    LEFT JOIN order_items oi ON p.id = oi.product_id
                    LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'completed'
                    GROUP BY c.id, c.name
                """
                    )
                )

                await db.commit()

                logger.info("✓ Updated aggregation tables")

                return {
                    "status": "success",
                    "tables_updated": ["agg_hourly_metrics", "agg_category_performance"],
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to update aggregation tables: {e}")
                await db.rollback()
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_update_agg_tables())


@celery_app.task(name="src.tasks.maintenance_tasks.check_database_health")
def check_database_health() -> dict[str, Any]:
    """
    Check database health and performance.

    Checks: connection pool, slow queries, table sizes, index usage.
    """
    import asyncio

    async def _check_health():
        async with AsyncSessionLocal() as db:
            try:
                health_checks = {}

                # Check connection pool
                result = await db.execute(
                    text(
                        """
                    SELECT count(*) as active_connections
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                """
                    )
                )
                health_checks["active_connections"] = result.scalar()

                # Check table sizes
                result = await db.execute(
                    text(
                        """
                    SELECT
                        schemaname,
                        tablename,
                        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    LIMIT 10
                """
                    )
                )
                health_checks["largest_tables"] = [dict(row) for row in result.fetchall()]

                # Check index usage
                result = await db.execute(
                    text(
                        """
                    SELECT
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan as index_scans
                    FROM pg_stat_user_indexes
                    WHERE idx_scan = 0
                      AND schemaname = 'public'
                    LIMIT 10
                """
                    )
                )
                health_checks["unused_indexes"] = [dict(row) for row in result.fetchall()]

                logger.info("✓ Database health check completed")

                return {
                    "status": "success",
                    "health_checks": health_checks,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed database health check: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_check_health())


@celery_app.task(name="src.tasks.maintenance_tasks.reindex_tables")
def reindex_tables() -> dict[str, Any]:
    """
    Reindex all tables to improve query performance.

    Runs monthly on 1st at midnight.
    """
    import asyncio

    async def _reindex():
        async with AsyncSessionLocal() as db:
            try:
                # Reindex all tables
                await db.execute(text("REINDEX DATABASE CONCURRENTLY"))

                logger.info("✓ Reindexed all tables")

                return {
                    "status": "success",
                    "message": "All tables reindexed",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to reindex tables: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_reindex())

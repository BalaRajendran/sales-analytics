"""
Notification background tasks.

Tasks for alerts, notifications, and monitoring.
"""

import logging
from datetime import datetime
from typing import Any

from src.celery_app import celery_app
from src.core.database import AsyncSessionLocal
from src.services.customer_service import customer_service
from src.services.product_service import product_service

logger = logging.getLogger(__name__)


@celery_app.task(name="src.tasks.notification_tasks.check_low_stock_products")
def check_low_stock_products() -> dict[str, Any]:
    """
    Check for low stock products and send alerts.

    Runs daily at 9 AM.
    Threshold: 10 units or less.
    """
    import asyncio

    async def _check_stock():
        async with AsyncSessionLocal() as db:
            try:
                # Get low stock products
                low_stock = await product_service.get_low_stock_products(
                    db, threshold=10, limit=100
                )

                out_of_stock = await product_service.get_out_of_stock_products(db, limit=100)

                alert_data = {
                    "low_stock_count": len(low_stock),
                    "out_of_stock_count": len(out_of_stock),
                    "low_stock_products": [
                        {
                            "id": str(p.id),
                            "name": p.name,
                            "stock_quantity": p.stock_quantity,
                        }
                        for p in low_stock[:10]  # Top 10
                    ],
                    "out_of_stock_products": [
                        {
                            "id": str(p.id),
                            "name": p.name,
                        }
                        for p in out_of_stock[:10]  # Top 10
                    ],
                }

                logger.info(
                    f"✓ Stock check: {len(low_stock)} low, {len(out_of_stock)} out of stock"
                )

                # TODO: Send email/Slack notification
                if len(low_stock) > 0 or len(out_of_stock) > 0:
                    logger.warning(
                        f"⚠️ Stock alerts: {len(low_stock)} low, {len(out_of_stock)} OOS"
                    )

                return {
                    "status": "success",
                    "alerts": alert_data,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed stock check: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_check_stock())


@celery_app.task(name="src.tasks.notification_tasks.identify_at_risk_customers")
def identify_at_risk_customers() -> dict[str, Any]:
    """
    Identify customers at risk of churning.

    Runs daily.
    Identifies customers with no orders in 90+ days.
    """
    import asyncio

    async def _identify_at_risk():
        async with AsyncSessionLocal() as db:
            try:
                # Get at-risk customers
                at_risk = await customer_service.get_at_risk_customers(db, days=90)

                alert_data = {
                    "at_risk_count": len(at_risk),
                    "customers": [
                        {
                            "id": str(c.id),
                            "name": c.name,
                            "email": c.email,
                            "segment": c.segment,
                            "lifetime_value": float(c.total_lifetime_value or 0),
                        }
                        for c in at_risk[:20]  # Top 20
                    ],
                }

                logger.info(f"✓ Identified {len(at_risk)} at-risk customers")

                # TODO: Send re-engagement campaign notification
                if len(at_risk) > 0:
                    logger.info(f"📧 Re-engagement needed for {len(at_risk)} customers")

                return {
                    "status": "success",
                    "alerts": alert_data,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed at-risk identification: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_identify_at_risk())


@celery_app.task(name="src.tasks.notification_tasks.send_daily_summary")
def send_daily_summary() -> dict[str, Any]:
    """
    Send daily summary email/notification.

    Runs daily at 8 AM.
    Summary of yesterday's performance.
    """
    import asyncio
    from datetime import timedelta

    async def _send_summary():
        async with AsyncSessionLocal() as db:
            try:
                from src.services.analytics_service import analytics_service

                # Yesterday's date range
                today = datetime.utcnow().date()
                yesterday = today - timedelta(days=1)
                start_date = datetime.combine(yesterday, datetime.min.time())
                end_date = datetime.combine(yesterday, datetime.max.time())

                # Get metrics
                revenue_metrics = await analytics_service.get_revenue_metrics(
                    db, start_date, end_date
                )
                order_metrics = await analytics_service.get_order_metrics(
                    db, start_date, end_date
                )

                summary = {
                    "date": yesterday.isoformat(),
                    "revenue": revenue_metrics,
                    "orders": order_metrics,
                }

                logger.info(f"✓ Daily summary for {yesterday}")

                # TODO: Send email/Slack notification
                logger.info(
                    f"📊 Yesterday: ${revenue_metrics['total_revenue']} revenue, "
                    f"{order_metrics['total_orders']} orders"
                )

                return {
                    "status": "success",
                    "summary": summary,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to send daily summary: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_send_summary())


@celery_app.task(name="src.tasks.notification_tasks.alert_high_value_order")
def alert_high_value_order(order_id: str) -> dict[str, Any]:
    """
    Send alert for high-value orders.

    Triggered when order > $10,000.
    """
    import asyncio
    from uuid import UUID

    async def _alert():
        async with AsyncSessionLocal() as db:
            try:
                from src.services.order_service import order_service

                order = await order_service.get_order_by_id(db, UUID(order_id))

                if not order:
                    return {
                        "status": "error",
                        "error": "Order not found",
                    }

                alert_data = {
                    "order_id": str(order.id),
                    "customer_id": str(order.customer_id),
                    "total_amount": float(order.total_amount),
                    "order_date": order.order_date.isoformat(),
                }

                logger.info(f"🎉 High-value order: ${order.total_amount}")

                # TODO: Send notification to sales team

                return {
                    "status": "success",
                    "alert": alert_data,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed to alert high-value order: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_alert())


@celery_app.task(name="src.tasks.notification_tasks.monitor_cache_performance")
def monitor_cache_performance() -> dict[str, Any]:
    """
    Monitor cache hit rates and performance.

    Runs hourly.
    Alerts if hit rate < 70%.
    """
    import asyncio

    async def _monitor():
        try:
            from src.core.cache import cache_manager

            # Get cache stats
            stats = await cache_manager.get_stats()

            total_requests = stats["hits"] + stats["misses"]
            hit_rate = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0

            performance = {
                "hit_rate_percentage": round(hit_rate, 2),
                "cache_hits": stats["hits"],
                "cache_misses": stats["misses"],
                "total_requests": total_requests,
                "target_hit_rate": 80.0,
                "status": "healthy" if hit_rate >= 70 else "degraded",
            }

            if hit_rate < 70:
                logger.warning(f"⚠️ Low cache hit rate: {hit_rate:.2f}%")
            else:
                logger.info(f"✓ Cache hit rate: {hit_rate:.2f}%")

            return {
                "status": "success",
                "performance": performance,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed cache monitoring: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    return asyncio.run(_monitor())


@celery_app.task(name="src.tasks.notification_tasks.weekly_performance_report")
def weekly_performance_report() -> dict[str, Any]:
    """
    Generate and send weekly performance report.

    Runs every Monday at 8 AM.
    """
    import asyncio
    from datetime import timedelta

    async def _weekly_report():
        async with AsyncSessionLocal() as db:
            try:
                from src.services.analytics_service import analytics_service

                # Last 7 days
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=7)

                # Get metrics
                revenue_metrics = await analytics_service.get_revenue_metrics(
                    db, start_date, end_date
                )
                order_metrics = await analytics_service.get_order_metrics(
                    db, start_date, end_date
                )
                top_products = await analytics_service.get_top_products(
                    db, start_date, end_date, limit=5
                )
                top_customers = await analytics_service.get_top_customers(
                    db, start_date, end_date, limit=5
                )

                report = {
                    "period": "last_7_days",
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "revenue": revenue_metrics,
                    "orders": order_metrics,
                    "top_products": top_products,
                    "top_customers": top_customers,
                }

                logger.info("✓ Generated weekly performance report")

                # TODO: Send email/Slack notification
                logger.info(
                    f"📈 Week: ${revenue_metrics['total_revenue']} revenue, "
                    f"{order_metrics['total_orders']} orders"
                )

                return {
                    "status": "success",
                    "report": report,
                    "timestamp": datetime.utcnow().isoformat(),
                }

            except Exception as e:
                logger.error(f"Failed weekly report: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

    return asyncio.run(_weekly_report())

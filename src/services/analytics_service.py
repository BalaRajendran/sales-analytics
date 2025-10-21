"""
Analytics service for dashboard metrics and reporting.

This service handles all analytics calculations and queries,
utilizing materialized views and aggregation tables for performance.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache_decorators import cached
from src.core.config import settings
from src.models.category import Category
from src.models.customer import Customer
from src.models.order import Order
from src.models.order_item import OrderItem
from src.models.product import Product
from src.models.sales_rep import SalesRepresentative


class AnalyticsService:
    """Service for analytics and reporting operations."""

    @staticmethod
    @cached(key_prefix="analytics:revenue_metrics", ttl=settings.CACHE_TTL_DASHBOARD)
    async def get_revenue_metrics(
        db: AsyncSession, start_date: datetime, end_date: datetime
    ) -> dict:
        """
        Get revenue metrics for date range.

        Returns total revenue, profit, and growth rates.
        """
        # Query current period revenue
        current_stmt = (
            select(
                func.sum(Order.total_amount).label("revenue"),
                func.count(Order.id).label("orders_count"),
            )
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
        )

        current_result = await db.execute(current_stmt)
        current_row = current_result.one()

        # Query previous period for growth calculation
        period_delta = end_date - start_date
        prev_start = start_date - period_delta
        prev_end = start_date

        prev_stmt = (
            select(func.sum(Order.total_amount).label("revenue"))
            .where(Order.order_date >= prev_start)
            .where(Order.order_date < prev_end)
            .where(Order.status == "completed")
        )

        prev_result = await db.execute(prev_stmt)
        prev_revenue = prev_result.scalar() or Decimal("0.00")

        # Calculate metrics
        current_revenue = current_row.revenue or Decimal("0.00")
        current_profit = current_revenue * Decimal("0.3")  # Simplified 30% margin

        # Calculate growth rate
        revenue_growth = None
        if prev_revenue > 0:
            revenue_growth = float((current_revenue - prev_revenue) / prev_revenue * 100)

        return {
            "total_revenue": current_revenue,
            "total_profit": current_profit,
            "profit_margin_percentage": 30.0,
            "revenue_growth": revenue_growth,
            "profit_growth": revenue_growth,  # Same as revenue growth for simplified model
        }

    @staticmethod
    @cached(key_prefix="analytics:order_metrics", ttl=settings.CACHE_TTL_DASHBOARD)
    async def get_order_metrics(
        db: AsyncSession, start_date: datetime, end_date: datetime
    ) -> dict:
        """
        Get order metrics for date range.

        Returns order counts by status and average order value.
        """
        stmt = (
            select(
                func.count(Order.id).label("total"),
                func.sum(func.case((Order.status == "completed", 1), else_=0)).label(
                    "completed"
                ),
                func.sum(func.case((Order.status == "pending", 1), else_=0)).label("pending"),
                func.sum(func.case((Order.status == "cancelled", 1), else_=0)).label(
                    "cancelled"
                ),
                func.avg(Order.total_amount).label("avg_value"),
            )
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
        )

        result = await db.execute(stmt)
        row = result.one()

        # Calculate growth
        period_delta = end_date - start_date
        prev_start = start_date - period_delta

        prev_stmt = (
            select(func.count(Order.id))
            .where(Order.order_date >= prev_start)
            .where(Order.order_date < start_date)
        )

        prev_result = await db.execute(prev_stmt)
        prev_count = prev_result.scalar() or 0

        orders_growth = None
        if prev_count > 0 and row.total:
            orders_growth = float((row.total - prev_count) / prev_count * 100)

        return {
            "total_orders": row.total or 0,
            "completed_orders": row.completed or 0,
            "pending_orders": row.pending or 0,
            "cancelled_orders": row.cancelled or 0,
            "avg_order_value": row.avg_value or Decimal("0.00"),
            "orders_growth": orders_growth,
        }

    @staticmethod
    @cached(key_prefix="analytics:top_products", ttl=settings.CACHE_TTL_PRODUCTS)
    async def get_top_products(
        db: AsyncSession, start_date: datetime, end_date: datetime, limit: int = 10
    ) -> list[dict]:
        """
        Get top performing products by revenue.

        Uses joins to aggregate order items.
        """
        stmt = (
            select(
                Product.id.label("product_id"),
                Product.name.label("product_name"),
                Category.name.label("category_name"),
                func.count(OrderItem.id).label("times_sold"),
                func.sum(OrderItem.total_price).label("revenue"),
                func.sum(
                    OrderItem.quantity * (OrderItem.unit_price - Product.cost_price)
                ).label("profit"),
                Product.stock_quantity,
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .join(Category, Product.category_id == Category.id)
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
            .group_by(Product.id, Product.name, Category.name, Product.stock_quantity)
            .order_by(func.sum(OrderItem.total_price).desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                "product_id": row.product_id,
                "product_name": row.product_name,
                "category_name": row.category_name,
                "times_sold": row.times_sold,
                "total_revenue": row.revenue or Decimal("0.00"),
                "total_profit": row.profit or Decimal("0.00"),
                "profit_margin_percentage": (
                    float(row.profit / row.revenue * 100) if row.revenue > 0 else 0.0
                ),
                "stock_quantity": row.stock_quantity,
                "revenue_rank": idx + 1,
            }
            for idx, row in enumerate(rows)
        ]

    @staticmethod
    @cached(key_prefix="analytics:top_categories", ttl=settings.CACHE_TTL_PRODUCTS)
    async def get_top_categories(
        db: AsyncSession, start_date: datetime, end_date: datetime, limit: int = 10
    ) -> list[dict]:
        """
        Get top performing categories by revenue.
        """
        stmt = (
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.count(func.distinct(Product.id)).label("products_count"),
                func.sum(OrderItem.total_price).label("revenue"),
                func.sum(
                    OrderItem.quantity * (OrderItem.unit_price - Product.cost_price)
                ).label("profit"),
            )
            .join(Product, Category.id == Product.category_id)
            .join(OrderItem, Product.id == OrderItem.product_id)
            .join(Order, OrderItem.order_id == Order.id)
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
            .group_by(Category.id, Category.name)
            .order_by(func.sum(OrderItem.total_price).desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        total_revenue = sum(row.revenue for row in rows) or Decimal("0.00")

        return [
            {
                "category_id": row.category_id,
                "category_name": row.category_name,
                "products_count": row.products_count,
                "total_revenue": row.revenue or Decimal("0.00"),
                "total_profit": row.profit or Decimal("0.00"),
                "profit_margin_percentage": (
                    float(row.profit / row.revenue * 100) if row.revenue > 0 else 0.0
                ),
                "revenue_contribution_percentage": (
                    float(row.revenue / total_revenue * 100) if total_revenue > 0 else 0.0
                ),
            }
            for row in rows
        ]

    @staticmethod
    @cached(key_prefix="analytics:top_customers", ttl=settings.CACHE_TTL_CUSTOMERS)
    async def get_top_customers(
        db: AsyncSession, start_date: datetime, end_date: datetime, limit: int = 10
    ) -> list[dict]:
        """
        Get top customers by revenue.
        """
        stmt = (
            select(
                Customer.id.label("customer_id"),
                Customer.name.label("customer_name"),
                Customer.email.label("customer_email"),
                Customer.segment,
                func.count(Order.id).label("orders"),
                func.sum(Order.total_amount).label("revenue"),
                func.avg(Order.total_amount).label("avg_order"),
                Customer.total_lifetime_value,
                func.max(Order.order_date).label("last_order"),
            )
            .join(Order, Customer.id == Order.customer_id)
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
            .group_by(Customer.id, Customer.name, Customer.email, Customer.segment)
            .order_by(func.sum(Order.total_amount).desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                "customer_id": row.customer_id,
                "customer_name": row.customer_name,
                "customer_email": row.customer_email,
                "segment": row.segment,
                "total_orders": row.orders,
                "total_revenue": row.revenue or Decimal("0.00"),
                "avg_order_value": row.avg_order or Decimal("0.00"),
                "lifetime_value": row.total_lifetime_value or Decimal("0.00"),
                "last_order_date": row.last_order,
            }
            for row in rows
        ]

    @staticmethod
    @cached(key_prefix="analytics:top_sales_reps", ttl=settings.CACHE_TTL_CUSTOMERS)
    async def get_top_sales_reps(
        db: AsyncSession, start_date: datetime, end_date: datetime, limit: int = 10
    ) -> list[dict]:
        """
        Get top sales representatives by revenue.
        """
        stmt = (
            select(
                SalesRepresentative.id.label("sales_rep_id"),
                SalesRepresentative.name.label("sales_rep_name"),
                SalesRepresentative.region,
                func.sum(Order.total_amount).label("sales"),
                func.count(Order.id).label("orders"),
                func.avg(Order.total_amount).label("avg_order"),
                SalesRepresentative.commission_rate,
            )
            .join(Order, SalesRepresentative.id == Order.sales_rep_id)
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
            .group_by(
                SalesRepresentative.id,
                SalesRepresentative.name,
                SalesRepresentative.region,
                SalesRepresentative.commission_rate,
            )
            .order_by(func.sum(Order.total_amount).desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        rows = result.all()

        total_revenue = sum(row.sales for row in rows) or Decimal("0.00")

        return [
            {
                "sales_rep_id": row.sales_rep_id,
                "sales_rep_name": row.sales_rep_name,
                "region": row.region,
                "total_sales": row.sales or Decimal("0.00"),
                "total_orders": row.orders,
                "avg_order_value": row.avg_order or Decimal("0.00"),
                "commission_earned": (
                    row.sales * row.commission_rate / 100
                    if row.commission_rate
                    else Decimal("0.00")
                ),
                "revenue_contribution_percentage": (
                    float(row.sales / total_revenue * 100) if total_revenue > 0 else 0.0
                ),
            }
            for row in rows
        ]

    @staticmethod
    @cached(key_prefix="analytics:revenue_trend", ttl=settings.CACHE_TTL_TRENDS)
    async def get_revenue_trend(
        db: AsyncSession, start_date: datetime, end_date: datetime
    ) -> dict:
        """
        Get revenue trend over time (daily aggregation).
        """
        stmt = (
            select(
                func.date_trunc("day", Order.order_date).label("date"),
                func.sum(Order.total_amount).label("revenue"),
            )
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
            .group_by(func.date_trunc("day", Order.order_date))
            .order_by(func.date_trunc("day", Order.order_date))
        )

        result = await db.execute(stmt)
        rows = result.all()

        data_points = [
            {
                "date": row.date,
                "value": row.revenue or Decimal("0.00"),
                "label": row.date.strftime("%Y-%m-%d"),
            }
            for row in rows
        ]

        total = sum(dp["value"] for dp in data_points)
        average = total / len(data_points) if data_points else Decimal("0.00")

        # Calculate trend direction
        if len(data_points) >= 2:
            first_half = sum(dp["value"] for dp in data_points[: len(data_points) // 2])
            second_half = sum(dp["value"] for dp in data_points[len(data_points) // 2 :])
            if second_half > first_half * Decimal("1.1"):
                trend_direction = "up"
            elif second_half < first_half * Decimal("0.9"):
                trend_direction = "down"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"

        # Calculate growth rate
        growth_rate = None
        if len(data_points) >= 2:
            first_value = data_points[0]["value"]
            last_value = data_points[-1]["value"]
            if first_value > 0:
                growth_rate = float((last_value - first_value) / first_value * 100)

        return {
            "period": "daily",
            "data_points": data_points,
            "total": total,
            "average": average,
            "growth_rate": growth_rate,
            "trend_direction": trend_direction,
        }

    @staticmethod
    @cached(key_prefix="analytics:order_trend", ttl=settings.CACHE_TTL_TRENDS)
    async def get_order_trend(
        db: AsyncSession, start_date: datetime, end_date: datetime
    ) -> dict:
        """
        Get order count trend over time (daily aggregation).
        """
        stmt = (
            select(
                func.date_trunc("day", Order.order_date).label("date"),
                func.count(Order.id).label("orders"),
            )
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .group_by(func.date_trunc("day", Order.order_date))
            .order_by(func.date_trunc("day", Order.order_date))
        )

        result = await db.execute(stmt)
        rows = result.all()

        data_points = [
            {
                "date": row.date,
                "value": Decimal(str(row.orders)),
                "label": row.date.strftime("%Y-%m-%d"),
            }
            for row in rows
        ]

        total = sum(dp["value"] for dp in data_points)
        average = total / len(data_points) if data_points else Decimal("0.00")

        # Calculate trend direction
        if len(data_points) >= 2:
            first_half_avg = (
                sum(dp["value"] for dp in data_points[: len(data_points) // 2])
                / len(data_points[: len(data_points) // 2])
            )
            second_half_avg = (
                sum(dp["value"] for dp in data_points[len(data_points) // 2 :])
                / len(data_points[len(data_points) // 2 :])
            )
            if second_half_avg > first_half_avg * Decimal("1.1"):
                trend_direction = "up"
            elif second_half_avg < first_half_avg * Decimal("0.9"):
                trend_direction = "down"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"

        return {
            "period": "daily",
            "data_points": data_points,
            "total": total,
            "average": average,
            "trend_direction": trend_direction,
        }

    @staticmethod
    @cached(key_prefix="analytics:realtime_metrics", ttl=settings.CACHE_TTL_REALTIME)
    async def get_realtime_metrics(db: AsyncSession) -> dict:
        """
        Get real-time metrics for today.
        """
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())

        # Query today's metrics
        stmt = (
            select(
                func.count(Order.id).label("orders_count"),
                func.sum(Order.total_amount).label("revenue"),
                func.avg(Order.total_amount).label("avg_order"),
            )
            .where(Order.order_date >= start_of_day)
            .where(Order.status == "completed")
        )

        result = await db.execute(stmt)
        row = result.one()

        # Get pending orders
        pending_stmt = select(func.count(Order.id)).where(Order.status == "pending")
        pending_result = await db.execute(pending_stmt)
        pending_count = pending_result.scalar() or 0

        return {
            "active_users": 0,  # Placeholder - implement with session tracking
            "pending_orders": pending_count,
            "revenue_today": row.revenue or Decimal("0.00"),
            "orders_today": row.orders_count or 0,
            "avg_order_value_today": row.avg_order or Decimal("0.00"),
            "top_selling_product_today": None,  # TODO: Implement
            "timestamp": datetime.utcnow(),
        }

    @staticmethod
    @cached(key_prefix="analytics:profit_analysis", ttl=settings.CACHE_TTL_TRENDS)
    async def get_profit_analysis(
        db: AsyncSession, start_date: datetime, end_date: datetime
    ) -> dict:
        """
        Get detailed profit analysis.
        """
        stmt = (
            select(
                func.sum(OrderItem.total_price).label("revenue"),
                func.sum(OrderItem.quantity * Product.cost_price).label("cost"),
            )
            .join(Order, OrderItem.order_id == Order.id)
            .join(Product, OrderItem.product_id == Product.id)
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
        )

        result = await db.execute(stmt)
        row = result.one()

        total_revenue = row.revenue or Decimal("0.00")
        total_cost = row.cost or Decimal("0.00")
        total_profit = total_revenue - total_cost
        profit_margin = float(total_profit / total_revenue * 100) if total_revenue > 0 else 0.0

        return {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "profit_margin_percentage": profit_margin,
        }

    @staticmethod
    @cached(key_prefix="analytics:regional_performance", ttl=settings.CACHE_TTL_TRENDS)
    async def get_regional_performance(
        db: AsyncSession, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """
        Get performance metrics by region.
        """
        stmt = (
            select(
                SalesRepresentative.region,
                func.sum(Order.total_amount).label("revenue"),
                func.count(Order.id).label("orders"),
                func.count(func.distinct(SalesRepresentative.id)).label("reps_count"),
                func.avg(Order.total_amount).label("avg_order"),
            )
            .join(Order, SalesRepresentative.id == Order.sales_rep_id)
            .where(Order.order_date >= start_date)
            .where(Order.order_date <= end_date)
            .where(Order.status == "completed")
            .where(SalesRepresentative.region.isnot(None))
            .group_by(SalesRepresentative.region)
            .order_by(func.sum(Order.total_amount).desc())
        )

        result = await db.execute(stmt)
        rows = result.all()

        total_revenue = sum(row.revenue for row in rows) or Decimal("0.00")

        return [
            {
                "region": row.region or "Unknown",
                "total_revenue": row.revenue or Decimal("0.00"),
                "total_orders": row.orders,
                "sales_reps_count": row.reps_count,
                "avg_order_value": row.avg_order or Decimal("0.00"),
                "revenue_contribution_percentage": (
                    float(row.revenue / total_revenue * 100) if total_revenue > 0 else 0.0
                ),
            }
            for row in rows
        ]

    @staticmethod
    @cached(
        key_prefix="analytics:customer_segment_distribution", ttl=settings.CACHE_TTL_CUSTOMERS
    )
    async def get_customer_segment_distribution(db: AsyncSession) -> list[dict]:
        """
        Get customer distribution by segment.
        """
        stmt = (
            select(
                Customer.segment,
                func.count(Customer.id).label("count"),
                func.sum(Customer.total_lifetime_value).label("revenue"),
                func.avg(Customer.total_lifetime_value).label("avg_ltv"),
            )
            .where(Customer.segment.isnot(None))
            .group_by(Customer.segment)
            .order_by(func.count(Customer.id).desc())
        )

        result = await db.execute(stmt)
        rows = result.all()

        total_customers = sum(row.count for row in rows)

        return [
            {
                "segment": row.segment,
                "customer_count": row.count,
                "total_revenue": row.revenue or Decimal("0.00"),
                "avg_lifetime_value": row.avg_ltv or Decimal("0.00"),
                "percentage": (row.count / total_customers * 100) if total_customers > 0 else 0.0,
            }
            for row in rows
        ]


# Singleton instance
analytics_service = AnalyticsService()

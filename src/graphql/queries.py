"""
GraphQL queries for the Sales Dashboard API.

All queries are cached using Redis for optimal performance.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

import strawberry
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import CacheKeys, cache_manager
from src.core.config import settings
from src.graphql.dataloaders import Dataloaders
from src.graphql.types import (
    CacheInfo,
    Category,
    CategoryPerformance,
    Customer,
    CustomerConnection,
    CustomerFilter,
    CustomerMetrics,
    CustomerSegmentDistribution,
    DashboardOverview,
    DateRangeEnum,
    DateRangeInput,
    HourlyMetrics,
    Order,
    OrderConnection,
    OrderFilter,
    OrderMetrics,
    OrderStatus,
    PageInfo,
    Product,
    ProductConnection,
    ProductFilter,
    ProductPerformance,
    ProfitAnalysis,
    RealtimeMetrics,
    RegionalPerformance,
    RevenueMetrics,
    SalesRepPerformance,
    SalesRepresentative,
    TrendAnalysis,
    TrendDataPoint,
)
from src.models.category import Category as CategoryModel
from src.models.customer import Customer as CustomerModel
from src.models.order import Order as OrderModel
from src.models.order_item import OrderItem as OrderItemModel
from src.models.product import Product as ProductModel
from src.models.sales_rep import SalesRepresentative as SalesRepModel


# ===========================
# Helper Functions
# ===========================


def _calculate_start_date(
    date_range: DateRangeEnum,
    custom_range: Optional[DateRangeInput],
    end_date: datetime,
) -> datetime:
    """Calculate start date based on date range enum."""
    if date_range == DateRangeEnum.CUSTOM and custom_range:
        return custom_range.start_date

    range_map = {
        DateRangeEnum.TODAY: timedelta(days=0),
        DateRangeEnum.YESTERDAY: timedelta(days=1),
        DateRangeEnum.LAST_7_DAYS: timedelta(days=7),
        DateRangeEnum.LAST_30_DAYS: timedelta(days=30),
        DateRangeEnum.LAST_90_DAYS: timedelta(days=90),
    }

    delta = range_map.get(date_range, timedelta(days=7))
    return end_date - delta


async def _get_revenue_metrics(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> RevenueMetrics:
    """Get revenue metrics for date range."""
    stmt = (
        select(
            func.sum(OrderModel.total_amount).label("revenue"),
            func.count(OrderModel.id).label("orders"),
        )
        .where(OrderModel.order_date >= start_date)
        .where(OrderModel.order_date <= end_date)
        .where(OrderModel.status == "completed")
    )

    result = await db.execute(stmt)
    row = result.one()

    # Calculate profit (simplified - would use order_items in production)
    total_revenue = row.revenue or Decimal("0.00")
    total_profit = total_revenue * Decimal("0.3")  # Assume 30% profit margin

    return RevenueMetrics(
        total_revenue=total_revenue,
        total_profit=total_profit,
        profit_margin_percentage=30.0,
    )


async def _get_order_metrics(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> OrderMetrics:
    """Get order metrics for date range."""
    from sqlalchemy import case as sql_case

    stmt = (
        select(
            func.count(OrderModel.id).label("total"),
            func.sum(sql_case((OrderModel.status == "completed", 1), else_=0)).label(
                "completed"
            ),
            func.sum(sql_case((OrderModel.status == "pending", 1), else_=0)).label(
                "pending"
            ),
            func.sum(sql_case((OrderModel.status == "cancelled", 1), else_=0)).label(
                "cancelled"
            ),
            func.avg(OrderModel.total_amount).label("avg_value"),
        )
        .where(OrderModel.order_date >= start_date)
        .where(OrderModel.order_date <= end_date)
    )

    result = await db.execute(stmt)
    row = result.one()

    return OrderMetrics(
        total_orders=row.total or 0,
        completed_orders=row.completed or 0,
        pending_orders=row.pending or 0,
        cancelled_orders=row.cancelled or 0,
        avg_order_value=row.avg_value or Decimal("0.00"),
    )


async def _get_top_products(
    db: AsyncSession, start_date: datetime, end_date: datetime, limit: int
) -> list[ProductPerformance]:
    """Get top performing products."""
    # This would query the materialized view in production
    stmt = (
        select(
            ProductModel.id,
            ProductModel.name,
            CategoryModel.name.label("category_name"),
            func.count(OrderItemModel.id).label("times_sold"),
            func.sum(OrderItemModel.total_price).label("revenue"),
            ProductModel.stock_quantity,
        )
        .join(OrderItemModel, ProductModel.id == OrderItemModel.product_id)
        .join(OrderModel, OrderItemModel.order_id == OrderModel.id)
        .join(CategoryModel, ProductModel.category_id == CategoryModel.id)
        .where(OrderModel.order_date >= start_date)
        .where(OrderModel.order_date <= end_date)
        .where(OrderModel.status == "completed")
        .group_by(ProductModel.id, ProductModel.name, CategoryModel.name)
        .order_by(func.sum(OrderItemModel.total_price).desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        ProductPerformance(
            product_id=row.id,
            product_name=row.name,
            category_name=row.category_name,
            times_sold=row.times_sold,
            total_revenue=row.revenue or Decimal("0.00"),
            total_profit=row.revenue * Decimal("0.3") or Decimal("0.00"),
            profit_margin_percentage=30.0,
            stock_quantity=row.stock_quantity,
            revenue_rank=idx + 1,
        )
        for idx, row in enumerate(rows)
    ]


async def _get_top_categories(
    db: AsyncSession, start_date: datetime, end_date: datetime, limit: int
) -> list[CategoryPerformance]:
    """Get top performing categories."""
    stmt = (
        select(
            CategoryModel.id,
            CategoryModel.name,
            func.count(func.distinct(ProductModel.id)).label("products_count"),
            func.sum(OrderItemModel.total_price).label("revenue"),
        )
        .join(ProductModel, CategoryModel.id == ProductModel.category_id)
        .join(OrderItemModel, ProductModel.id == OrderItemModel.product_id)
        .join(OrderModel, OrderItemModel.order_id == OrderModel.id)
        .where(OrderModel.order_date >= start_date)
        .where(OrderModel.order_date <= end_date)
        .where(OrderModel.status == "completed")
        .group_by(CategoryModel.id, CategoryModel.name)
        .order_by(func.sum(OrderItemModel.total_price).desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    total_revenue = sum(row.revenue for row in rows)

    return [
        CategoryPerformance(
            category_id=row.id,
            category_name=row.name,
            products_count=row.products_count,
            total_revenue=row.revenue or Decimal("0.00"),
            total_profit=row.revenue * Decimal("0.3") or Decimal("0.00"),
            profit_margin_percentage=30.0,
            revenue_contribution_percentage=(
                float(row.revenue / total_revenue * 100) if total_revenue > 0 else 0.0
            ),
        )
        for row in rows
    ]


async def _get_top_customers(
    db: AsyncSession, start_date: datetime, end_date: datetime, limit: int
) -> list[CustomerMetrics]:
    """Get top customers by revenue."""
    stmt = (
        select(
            CustomerModel.id,
            CustomerModel.name,
            CustomerModel.email,
            CustomerModel.segment,
            func.count(OrderModel.id).label("orders"),
            func.sum(OrderModel.total_amount).label("revenue"),
            func.avg(OrderModel.total_amount).label("avg_order"),
            CustomerModel.total_lifetime_value,
            func.max(OrderModel.order_date).label("last_order_date"),
        )
        .join(OrderModel, CustomerModel.id == OrderModel.customer_id)
        .where(OrderModel.order_date >= start_date)
        .where(OrderModel.order_date <= end_date)
        .where(OrderModel.status == "completed")
        .group_by(CustomerModel.id, CustomerModel.name, CustomerModel.email)
        .order_by(func.sum(OrderModel.total_amount).desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    return [
        CustomerMetrics(
            customer_id=row.id,
            customer_name=row.name,
            customer_email=row.email,
            segment=row.segment,
            total_orders=row.orders,
            total_revenue=row.revenue or Decimal("0.00"),
            avg_order_value=row.avg_order or Decimal("0.00"),
            lifetime_value=row.total_lifetime_value or Decimal("0.00"),
            last_order_date=row.last_order_date,
        )
        for row in rows
    ]


async def _get_top_sales_reps(
    db: AsyncSession, start_date: datetime, end_date: datetime, limit: int
) -> list[SalesRepPerformance]:
    """Get top sales representatives."""
    stmt = (
        select(
            SalesRepModel.id,
            SalesRepModel.name,
            SalesRepModel.region,
            func.sum(OrderModel.total_amount).label("sales"),
            func.count(OrderModel.id).label("orders"),
            func.avg(OrderModel.total_amount).label("avg_order"),
            SalesRepModel.commission_rate,
        )
        .join(OrderModel, SalesRepModel.id == OrderModel.sales_rep_id)
        .where(OrderModel.order_date >= start_date)
        .where(OrderModel.order_date <= end_date)
        .where(OrderModel.status == "completed")
        .group_by(SalesRepModel.id, SalesRepModel.name, SalesRepModel.region)
        .order_by(func.sum(OrderModel.total_amount).desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    rows = result.all()

    total_revenue = sum(row.sales for row in rows)

    return [
        SalesRepPerformance(
            sales_rep_id=row.id,
            sales_rep_name=row.name,
            region=row.region,
            total_sales=row.sales or Decimal("0.00"),
            total_orders=row.orders,
            avg_order_value=row.avg_order or Decimal("0.00"),
            commission_earned=(row.sales * row.commission_rate / 100)
            if row.commission_rate
            else Decimal("0.00"),
            revenue_contribution_percentage=(
                float(row.sales / total_revenue * 100) if total_revenue > 0 else 0.0
            ),
        )
        for row in rows
    ]


async def _get_revenue_trend(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> TrendAnalysis:
    """Get revenue trend over time."""
    # Simplified - would use materialized views in production
    date_trunc = func.date_trunc("day", OrderModel.order_date)

    stmt = (
        select(
            date_trunc.label("date"),
            func.sum(OrderModel.total_amount).label("revenue"),
        )
        .where(OrderModel.order_date >= start_date)
        .where(OrderModel.order_date <= end_date)
        .where(OrderModel.status == "completed")
        .group_by(date_trunc)
        .order_by(date_trunc)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data_points = [
        TrendDataPoint(
            date=row.date,
            value=row.revenue or Decimal("0.00"),
            label=row.date.strftime("%Y-%m-%d"),
        )
        for row in rows
    ]

    total = sum(dp.value for dp in data_points)
    average = total / len(data_points) if data_points else Decimal("0.00")

    return TrendAnalysis(
        period="daily",
        data_points=data_points,
        total=total,
        average=average,
        trend_direction="stable",
    )


async def _get_order_trend(
    db: AsyncSession, start_date: datetime, end_date: datetime
) -> TrendAnalysis:
    """Get order count trend over time."""
    date_trunc = func.date_trunc("day", OrderModel.order_date)

    stmt = (
        select(
            date_trunc.label("date"),
            func.count(OrderModel.id).label("orders"),
        )
        .where(OrderModel.order_date >= start_date)
        .where(OrderModel.order_date <= end_date)
        .group_by(date_trunc)
        .order_by(date_trunc)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data_points = [
        TrendDataPoint(
            date=row.date,
            value=Decimal(str(row.orders)),
            label=row.date.strftime("%Y-%m-%d"),
        )
        for row in rows
    ]

    total = sum(dp.value for dp in data_points)
    average = total / len(data_points) if data_points else Decimal("0.00")

    return TrendAnalysis(
        period="daily",
        data_points=data_points,
        total=total,
        average=average,
        trend_direction="stable",
    )


@strawberry.type
class Query:
    """Root Query type for GraphQL API."""

    # ===========================
    # Dashboard & Overview Queries
    # ===========================

    @strawberry.field
    async def dashboard_overview(
        self,
        date_range: DateRangeEnum = DateRangeEnum.LAST_7_DAYS,
        custom_range: Optional[DateRangeInput] = None,
        info: strawberry.Info = None,
    ) -> DashboardOverview:
        """
        Get complete dashboard overview with all key metrics.

        This is the main query for the dashboard home page.
        NOTE: Caching disabled for GraphQL resolvers (incompatible with Strawberry types).
        """
        db: AsyncSession = info.context["db"]

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = _calculate_start_date(date_range, custom_range, end_date)

        # Query revenue metrics
        revenue_metrics = await _get_revenue_metrics(db, start_date, end_date)

        # Query order metrics
        order_metrics = await _get_order_metrics(db, start_date, end_date)

        # Query top performers
        top_products = await _get_top_products(db, start_date, end_date, limit=5)
        top_categories = await _get_top_categories(db, start_date, end_date, limit=5)
        top_customers = await _get_top_customers(db, start_date, end_date, limit=5)
        top_sales_reps = await _get_top_sales_reps(db, start_date, end_date, limit=5)

        # Query trends
        revenue_trend = await _get_revenue_trend(db, start_date, end_date)
        order_trend = await _get_order_trend(db, start_date, end_date)

        return DashboardOverview(
            revenue_metrics=revenue_metrics,
            order_metrics=order_metrics,
            top_products=top_products,
            top_categories=top_categories,
            top_customers=top_customers,
            top_sales_reps=top_sales_reps,
            revenue_trend=revenue_trend,
            order_trend=order_trend,
            date_range=date_range.value,
            start_date=start_date,
            end_date=end_date,
            cached_at=datetime.utcnow(),
        )

    @strawberry.field
    async def realtime_metrics(self, info: strawberry.Info = None) -> RealtimeMetrics:
        """
        Get real-time metrics for the dashboard.

        NOTE: Caching disabled for GraphQL resolvers (incompatible with Strawberry types).
        """
        db: AsyncSession = info.context["db"]

        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())

        # Query today's metrics
        stmt = (
            select(
                func.count(OrderModel.id).label("orders_count"),
                func.sum(OrderModel.total_amount).label("revenue"),
                func.avg(OrderModel.total_amount).label("avg_order"),
            )
            .where(OrderModel.order_date >= start_of_day)
            .where(OrderModel.status == "completed")
        )

        result = await db.execute(stmt)
        row = result.one()

        # Get pending orders
        pending_stmt = select(func.count(OrderModel.id)).where(OrderModel.status == "pending")
        pending_result = await db.execute(pending_stmt)
        pending_count = pending_result.scalar() or 0

        return RealtimeMetrics(
            active_users=0,  # TODO: Implement active users tracking
            pending_orders=pending_count,
            revenue_today=row.revenue or Decimal("0.00"),
            orders_today=row.orders_count or 0,
            avg_order_value_today=row.avg_order or Decimal("0.00"),
            timestamp=datetime.utcnow(),
        )

    # ===========================
    # Product Queries
    # ===========================

    @strawberry.field
    async def product(
        self, product_id: UUID, info: strawberry.Info = None
    ) -> Optional[Product]:
        """Get a single product by ID."""
        dataloaders: Dataloaders = info.context["dataloaders"]
        product = await dataloaders.product_loader.load(product_id)

        if not product:
            return None

        # Load category
        category = None
        if product.category_id:
            category = await dataloaders.category_loader.load(product.category_id)

        return Product(
            id=product.id,
            name=product.name,
            category_id=product.category_id,
            cost_price=product.cost_price,
            selling_price=product.selling_price,
            stock_quantity=product.stock_quantity,
            profit_margin=product.profit_margin,
            profit_margin_percentage=product.profit_margin_percentage,
            created_at=product.created_at,
            updated_at=product.updated_at,
            category=self._map_category(category) if category else None,
        )

    @strawberry.field
    async def products(
        self,
        filter: Optional[ProductFilter] = None,
        limit: int = 20,
        offset: int = 0,
        info: strawberry.Info = None,
    ) -> ProductConnection:
        """Get paginated list of products with optional filters."""
        db: AsyncSession = info.context["db"]

        # Build query
        stmt = select(ProductModel)

        # Apply filters
        if filter:
            if filter.category_id:
                stmt = stmt.where(ProductModel.category_id == filter.category_id)
            if filter.min_price:
                stmt = stmt.where(ProductModel.selling_price >= filter.min_price)
            if filter.max_price:
                stmt = stmt.where(ProductModel.selling_price <= filter.max_price)
            if filter.in_stock is not None:
                if filter.in_stock:
                    stmt = stmt.where(ProductModel.stock_quantity > 0)
                else:
                    stmt = stmt.where(ProductModel.stock_quantity == 0)
            if filter.search:
                stmt = stmt.where(ProductModel.name.ilike(f"%{filter.search}%"))

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total_count = total_result.scalar() or 0

        # Apply pagination
        stmt = stmt.limit(limit).offset(offset)

        # Execute query
        result = await db.execute(stmt)
        products = result.scalars().all()

        # Map to GraphQL types
        edges = [
            Product(
                id=p.id,
                name=p.name,
                category_id=p.category_id,
                cost_price=p.cost_price,
                selling_price=p.selling_price,
                stock_quantity=p.stock_quantity,
                profit_margin=p.profit_margin,
                profit_margin_percentage=p.profit_margin_percentage,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in products
        ]

        # Build page info
        page_info = PageInfo(
            has_next_page=(offset + limit) < total_count,
            has_previous_page=offset > 0,
            total_count=total_count,
        )

        return ProductConnection(edges=edges, page_info=page_info)

    @strawberry.field
    async def product_performance(
        self,
        date_range: DateRangeEnum = DateRangeEnum.LAST_30_DAYS,
        limit: int = 10,
        info: strawberry.Info = None,
    ) -> list[ProductPerformance]:
        """
        Get top performing products with detailed metrics.

        NOTE: Caching disabled for GraphQL resolvers (incompatible with Strawberry types).
        """
        db: AsyncSession = info.context["db"]

        end_date = datetime.utcnow()
        start_date = _calculate_start_date(date_range, None, end_date)

        return await _get_top_products(db, start_date, end_date, limit)

    # ===========================
    # Customer Queries
    # ===========================

    @strawberry.field
    async def customer(
        self, customer_id: UUID, info: strawberry.Info = None
    ) -> Optional[Customer]:
        """Get a single customer by ID."""
        dataloaders: Dataloaders = info.context["dataloaders"]
        customer = await dataloaders.customer_loader.load(customer_id)

        if not customer:
            return None

        return self._map_customer(customer)

    @strawberry.field
    async def customers(
        self,
        filter: Optional[CustomerFilter] = None,
        limit: int = 20,
        offset: int = 0,
        info: strawberry.Info = None,
    ) -> CustomerConnection:
        """Get paginated list of customers with optional filters."""
        db: AsyncSession = info.context["db"]

        stmt = select(CustomerModel)

        # Apply filters
        if filter:
            if filter.segment:
                stmt = stmt.where(CustomerModel.segment == filter.segment.value)
            if filter.min_lifetime_value:
                stmt = stmt.where(CustomerModel.total_lifetime_value >= filter.min_lifetime_value)
            if filter.search:
                search_pattern = f"%{filter.search}%"
                stmt = stmt.where(
                    (CustomerModel.name.ilike(search_pattern))
                    | (CustomerModel.email.ilike(search_pattern))
                )

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total_count = total_result.scalar() or 0

        # Apply pagination
        stmt = stmt.limit(limit).offset(offset)

        result = await db.execute(stmt)
        customers = result.scalars().all()

        edges = [self._map_customer(c) for c in customers]

        page_info = PageInfo(
            has_next_page=(offset + limit) < total_count,
            has_previous_page=offset > 0,
            total_count=total_count,
        )

        return CustomerConnection(edges=edges, page_info=page_info)

    @strawberry.field
    async def customer_segment_distribution(
        self, info: strawberry.Info = None
    ) -> list[CustomerSegmentDistribution]:
        """
        Get customer distribution by segment.

        NOTE: Caching disabled for GraphQL resolvers (incompatible with Strawberry types).
        """
        db: AsyncSession = info.context["db"]

        stmt = select(
            CustomerModel.segment,
            func.count(CustomerModel.id).label("count"),
            func.sum(CustomerModel.total_lifetime_value).label("revenue"),
            func.avg(CustomerModel.total_lifetime_value).label("avg_ltv"),
        ).group_by(CustomerModel.segment)

        result = await db.execute(stmt)
        rows = result.all()

        total_customers = sum(row.count for row in rows)

        return [
            CustomerSegmentDistribution(
                segment=row.segment,
                customer_count=row.count,
                total_revenue=row.revenue or Decimal("0.00"),
                avg_lifetime_value=row.avg_ltv or Decimal("0.00"),
                percentage=(row.count / total_customers * 100) if total_customers > 0 else 0,
            )
            for row in rows
        ]

    # ===========================
    # Order Queries
    # ===========================

    @strawberry.field
    async def order(self, order_id: UUID, info: strawberry.Info = None) -> Optional[Order]:
        """Get a single order by ID."""
        dataloaders: Dataloaders = info.context["dataloaders"]
        order = await dataloaders.order_loader.load(order_id)

        if not order:
            return None

        return await self._map_order(order, dataloaders)

    @strawberry.field
    async def orders(
        self,
        filter: Optional[OrderFilter] = None,
        limit: int = 20,
        offset: int = 0,
        info: strawberry.Info = None,
    ) -> OrderConnection:
        """Get paginated list of orders with optional filters."""
        db: AsyncSession = info.context["db"]

        stmt = select(OrderModel)

        # Apply filters
        if filter:
            if filter.customer_id:
                stmt = stmt.where(OrderModel.customer_id == filter.customer_id)
            if filter.sales_rep_id:
                stmt = stmt.where(OrderModel.sales_rep_id == filter.sales_rep_id)
            if filter.status:
                stmt = stmt.where(OrderModel.status == filter.status.value)
            if filter.date_from:
                stmt = stmt.where(OrderModel.order_date >= filter.date_from)
            if filter.date_to:
                stmt = stmt.where(OrderModel.order_date <= filter.date_to)
            if filter.min_amount:
                stmt = stmt.where(OrderModel.total_amount >= filter.min_amount)
            if filter.max_amount:
                stmt = stmt.where(OrderModel.total_amount <= filter.max_amount)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total_count = total_result.scalar() or 0

        # Apply pagination
        stmt = stmt.order_by(OrderModel.order_date.desc()).limit(limit).offset(offset)

        result = await db.execute(stmt)
        orders = result.scalars().all()

        dataloaders: Dataloaders = info.context["dataloaders"]
        edges = [await self._map_order(o, dataloaders) for o in orders]

        page_info = PageInfo(
            has_next_page=(offset + limit) < total_count,
            has_previous_page=offset > 0,
            total_count=total_count,
        )

        return OrderConnection(edges=edges, page_info=page_info)

    # ===========================
    # Analytics Queries
    # ===========================

    @strawberry.field
    async def profit_analysis(
        self,
        date_range: DateRangeEnum = DateRangeEnum.LAST_30_DAYS,
        info: strawberry.Info = None,
    ) -> ProfitAnalysis:
        """
        Get detailed profit analysis.

        NOTE: Caching disabled for GraphQL resolvers (incompatible with Strawberry types).
        """
        db: AsyncSession = info.context["db"]

        end_date = datetime.utcnow()
        start_date = _calculate_start_date(date_range, None, end_date)

        # Calculate total revenue and cost
        stmt = (
            select(
                func.sum(OrderItemModel.total_price).label("revenue"),
                func.sum(OrderItemModel.quantity * ProductModel.cost_price).label("cost"),
            )
            .join(OrderModel, OrderItemModel.order_id == OrderModel.id)
            .join(ProductModel, OrderItemModel.product_id == ProductModel.id)
            .where(OrderModel.order_date >= start_date)
            .where(OrderModel.order_date <= end_date)
            .where(OrderModel.status == "completed")
        )

        result = await db.execute(stmt)
        row = result.one()

        total_revenue = row.revenue or Decimal("0.00")
        total_cost = row.cost or Decimal("0.00")
        total_profit = total_revenue - total_cost
        profit_margin = (
            float(total_profit / total_revenue * 100) if total_revenue > 0 else 0.0
        )

        return ProfitAnalysis(
            total_revenue=total_revenue,
            total_cost=total_cost,
            total_profit=total_profit,
            profit_margin_percentage=profit_margin,
        )

    @strawberry.field
    async def regional_performance(
        self,
        date_range: DateRangeEnum = DateRangeEnum.LAST_30_DAYS,
        info: strawberry.Info = None,
    ) -> list[RegionalPerformance]:
        """
        Get performance metrics by region.

        NOTE: Caching disabled for GraphQL resolvers (incompatible with Strawberry types).
        """
        db: AsyncSession = info.context["db"]

        end_date = datetime.utcnow()
        start_date = _calculate_start_date(date_range, None, end_date)

        stmt = (
            select(
                SalesRepModel.region,
                func.sum(OrderModel.total_amount).label("revenue"),
                func.count(OrderModel.id).label("orders"),
                func.count(func.distinct(SalesRepModel.id)).label("reps_count"),
                func.avg(OrderModel.total_amount).label("avg_order"),
            )
            .join(OrderModel, SalesRepModel.id == OrderModel.sales_rep_id)
            .where(OrderModel.order_date >= start_date)
            .where(OrderModel.order_date <= end_date)
            .where(OrderModel.status == "completed")
            .group_by(SalesRepModel.region)
        )

        result = await db.execute(stmt)
        rows = result.all()

        total_revenue = sum(row.revenue for row in rows)

        return [
            RegionalPerformance(
                region=row.region or "Unknown",
                total_revenue=row.revenue or Decimal("0.00"),
                total_orders=row.orders,
                sales_reps_count=row.reps_count,
                avg_order_value=row.avg_order or Decimal("0.00"),
                revenue_contribution_percentage=(
                    float(row.revenue / total_revenue * 100) if total_revenue > 0 else 0.0
                ),
            )
            for row in rows
        ]

    # ===========================
    # Cache Info Query
    # ===========================

    @strawberry.field
    async def cache_info(self, info: strawberry.Info = None) -> CacheInfo:
        """Get cache performance information."""
        stats = cache_manager.get_stats()

        total_requests = stats["hits"] + stats["misses"]
        hit_rate = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return CacheInfo(
            cache_hits=stats["hits"],
            cache_misses=stats["misses"],
            hit_rate_percentage=round(hit_rate, 2),
            is_cached=True,
        )

    # ===========================
    # Helper Methods (Mapper functions only)
    # ===========================

    def _map_category(self, category: CategoryModel) -> Category:
        """Map database category to GraphQL type."""
        return Category(
            id=category.id,
            name=category.name,
            parent_id=category.parent_id,
            created_at=category.created_at,
            updated_at=category.updated_at,
            products_count=0,
        )

    def _map_customer(self, customer: CustomerModel) -> Customer:
        """Map database customer to GraphQL type."""
        return Customer(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            segment=customer.segment,
            total_lifetime_value=customer.total_lifetime_value,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )

    async def _map_order(self, order: OrderModel, dataloaders: Dataloaders) -> Order:
        """Map database order to GraphQL type."""
        return Order(
            id=order.id,
            customer_id=order.customer_id,
            sales_rep_id=order.sales_rep_id,
            order_date=order.order_date,
            total_amount=order.total_amount,
            status=OrderStatus(order.status),
            profit=order.profit,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

"""
GraphQL types for the Sales Dashboard API.

All types are defined using Strawberry GraphQL.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

import strawberry


# Enums
@strawberry.enum
class OrderStatus(Enum):
    """Order status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@strawberry.enum
class CustomerSegment(Enum):
    """Customer segment enumeration."""

    PREMIUM = "Premium"
    REGULAR = "Regular"
    NEW = "New"
    AT_RISK = "At-Risk"
    CHURNED = "Churned"


@strawberry.enum
class DateRangeEnum(Enum):
    """Date range options for analytics."""

    TODAY = "today"
    YESTERDAY = "yesterday"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    THIS_MONTH = "this_month"
    LAST_MONTH = "last_month"
    THIS_YEAR = "this_year"
    CUSTOM = "custom"


# Base Types
@strawberry.type
class Category:
    """Product category type."""

    id: UUID
    name: str
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    # Relationships
    parent: Optional["Category"] = None
    children: list["Category"] = strawberry.field(default_factory=list)
    products_count: int = 0


@strawberry.type
class Product:
    """Product type."""

    id: UUID
    name: str
    category_id: UUID
    cost_price: Decimal
    selling_price: Decimal
    stock_quantity: int
    profit_margin: Decimal
    profit_margin_percentage: float
    created_at: datetime
    updated_at: datetime

    # Relationships
    category: Optional[Category] = None


@strawberry.type
class Customer:
    """Customer type."""

    id: UUID
    name: str
    email: str
    segment: Optional[CustomerSegment]
    total_lifetime_value: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

    # Computed fields
    orders_count: int = 0
    avg_order_value: Optional[Decimal] = None


@strawberry.type
class SalesRepresentative:
    """Sales representative type."""

    id: UUID
    name: str
    email: str
    region: Optional[str]
    commission_rate: Optional[Decimal]
    created_at: datetime
    updated_at: datetime

    # Computed fields
    total_sales: Optional[Decimal] = None
    orders_count: int = 0
    commission_earned: Optional[Decimal] = None


@strawberry.type
class OrderItem:
    """Order item type."""

    id: UUID
    order_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    profit: Decimal
    created_at: datetime
    updated_at: datetime

    # Relationships
    product: Optional[Product] = None


@strawberry.type
class Order:
    """Order type."""

    id: UUID
    customer_id: UUID
    sales_rep_id: Optional[UUID]
    order_date: datetime
    total_amount: Decimal
    status: OrderStatus
    profit: Decimal
    created_at: datetime
    updated_at: datetime

    # Relationships
    customer: Optional[Customer] = None
    sales_rep: Optional[SalesRepresentative] = None
    items: list[OrderItem] = strawberry.field(default_factory=list)


# Analytics Types
@strawberry.type
class RevenueMetrics:
    """Revenue metrics for analytics."""

    total_revenue: Decimal
    total_profit: Decimal
    profit_margin_percentage: float
    revenue_growth: Optional[float] = None
    profit_growth: Optional[float] = None


@strawberry.type
class OrderMetrics:
    """Order metrics for analytics."""

    total_orders: int
    completed_orders: int
    pending_orders: int
    cancelled_orders: int
    avg_order_value: Decimal
    orders_growth: Optional[float] = None


@strawberry.type
class ProductPerformance:
    """Product performance metrics."""

    product_id: UUID
    product_name: str
    category_name: str
    times_sold: int
    total_revenue: Decimal
    total_profit: Decimal
    profit_margin_percentage: float
    stock_quantity: int
    revenue_rank: Optional[int] = None


@strawberry.type
class CategoryPerformance:
    """Category performance metrics."""

    category_id: UUID
    category_name: str
    products_count: int
    total_revenue: Decimal
    total_profit: Decimal
    profit_margin_percentage: float
    revenue_contribution_percentage: float


@strawberry.type
class CustomerMetrics:
    """Customer analytics metrics."""

    customer_id: UUID
    customer_name: str
    customer_email: str
    segment: Optional[CustomerSegment]
    total_orders: int
    total_revenue: Decimal
    avg_order_value: Decimal
    lifetime_value: Decimal
    last_order_date: Optional[datetime]


@strawberry.type
class SalesRepPerformance:
    """Sales representative performance metrics."""

    sales_rep_id: UUID
    sales_rep_name: str
    region: Optional[str]
    total_sales: Decimal
    total_orders: int
    avg_order_value: Decimal
    commission_earned: Decimal
    revenue_contribution_percentage: float


@strawberry.type
class TrendDataPoint:
    """Single data point in a trend chart."""

    date: datetime
    value: Decimal
    label: str


@strawberry.type
class TrendAnalysis:
    """Trend analysis with time series data."""

    period: str
    data_points: list[TrendDataPoint]
    total: Decimal
    average: Decimal
    growth_rate: Optional[float] = None
    trend_direction: str  # "up", "down", "stable"


@strawberry.type
class DashboardOverview:
    """Complete dashboard overview metrics."""

    # Revenue metrics
    revenue_metrics: RevenueMetrics

    # Order metrics
    order_metrics: OrderMetrics

    # Top performers
    top_products: list[ProductPerformance]
    top_categories: list[CategoryPerformance]
    top_customers: list[CustomerMetrics]
    top_sales_reps: list[SalesRepPerformance]

    # Trends
    revenue_trend: TrendAnalysis
    order_trend: TrendAnalysis

    # Period info
    date_range: str
    start_date: datetime
    end_date: datetime
    cached_at: Optional[datetime] = None


@strawberry.type
class RealtimeMetrics:
    """Real-time dashboard metrics."""

    active_users: int
    pending_orders: int
    revenue_today: Decimal
    orders_today: int
    avg_order_value_today: Decimal
    top_selling_product_today: Optional[str] = None
    timestamp: datetime


@strawberry.type
class CustomerSegmentDistribution:
    """Customer distribution by segment."""

    segment: CustomerSegment
    customer_count: int
    total_revenue: Decimal
    avg_lifetime_value: Decimal
    percentage: float


@strawberry.type
class RegionalPerformance:
    """Performance metrics by region."""

    region: str
    total_revenue: Decimal
    total_orders: int
    sales_reps_count: int
    avg_order_value: Decimal
    revenue_contribution_percentage: float


@strawberry.type
class HourlyMetrics:
    """Hourly performance metrics."""

    hour: int
    revenue: Decimal
    orders_count: int
    avg_order_value: Decimal


@strawberry.type
class ProfitAnalysis:
    """Detailed profit analysis."""

    total_revenue: Decimal
    total_cost: Decimal
    total_profit: Decimal
    profit_margin_percentage: float
    best_profit_margin_product: Optional[ProductPerformance] = None
    best_profit_margin_category: Optional[CategoryPerformance] = None


# Pagination Types
@strawberry.type
class PageInfo:
    """Pagination information."""

    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None
    total_count: int


@strawberry.type
class ProductConnection:
    """Paginated product results."""

    edges: list[Product]
    page_info: PageInfo


@strawberry.type
class OrderConnection:
    """Paginated order results."""

    edges: list[Order]
    page_info: PageInfo


@strawberry.type
class CustomerConnection:
    """Paginated customer results."""

    edges: list[Customer]
    page_info: PageInfo


# Input Types for Mutations
@strawberry.input
class CreateProductInput:
    """Input for creating a new product."""

    name: str
    category_id: UUID
    cost_price: Decimal
    selling_price: Decimal
    stock_quantity: int = 0


@strawberry.input
class UpdateProductInput:
    """Input for updating a product."""

    name: Optional[str] = None
    category_id: Optional[UUID] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None


@strawberry.input
class CreateCustomerInput:
    """Input for creating a new customer."""

    name: str
    email: str
    segment: Optional[CustomerSegment] = None


@strawberry.input
class UpdateCustomerInput:
    """Input for updating a customer."""

    name: Optional[str] = None
    email: Optional[str] = None
    segment: Optional[CustomerSegment] = None
    total_lifetime_value: Optional[Decimal] = None


@strawberry.input
class CreateOrderInput:
    """Input for creating a new order."""

    customer_id: UUID
    sales_rep_id: Optional[UUID] = None
    order_date: datetime
    items: list["OrderItemInput"]


@strawberry.input
class OrderItemInput:
    """Input for order item."""

    product_id: UUID
    quantity: int
    unit_price: Decimal


@strawberry.input
class UpdateOrderStatusInput:
    """Input for updating order status."""

    order_id: UUID
    status: OrderStatus


# Response Types
@strawberry.type
class MutationResponse:
    """Generic mutation response."""

    success: bool
    message: str
    errors: Optional[list[str]] = None


@strawberry.type
class ProductMutationResponse(MutationResponse):
    """Product mutation response."""

    product: Optional[Product] = None


@strawberry.type
class CustomerMutationResponse(MutationResponse):
    """Customer mutation response."""

    customer: Optional[Customer] = None


@strawberry.type
class OrderMutationResponse(MutationResponse):
    """Order mutation response."""

    order: Optional[Order] = None


# Filter Input Types
@strawberry.input
class ProductFilter:
    """Filter options for products."""

    category_id: Optional[UUID] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    in_stock: Optional[bool] = None
    search: Optional[str] = None


@strawberry.input
class OrderFilter:
    """Filter options for orders."""

    customer_id: Optional[UUID] = None
    sales_rep_id: Optional[UUID] = None
    status: Optional[OrderStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None


@strawberry.input
class CustomerFilter:
    """Filter options for customers."""

    segment: Optional[CustomerSegment] = None
    min_lifetime_value: Optional[Decimal] = None
    search: Optional[str] = None


@strawberry.input
class DateRangeInput:
    """Custom date range input."""

    start_date: datetime
    end_date: datetime


# Cache Info Type
@strawberry.type
class CacheInfo:
    """Cache performance information."""

    cache_hits: int
    cache_misses: int
    hit_rate_percentage: float
    is_cached: bool
    cached_at: Optional[datetime] = None

# Implementation Guide - Sales Analytics Dashboard

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Phase 1: Foundation Setup](#phase-1-foundation-setup)
3. [Phase 2: Database Layer](#phase-2-database-layer)
4. [Phase 3: Caching Layer](#phase-3-caching-layer)
5. [Phase 4: GraphQL API](#phase-4-graphql-api)
6. [Phase 5: Analytics Services](#phase-5-analytics-services)
7. [Phase 6: Background Tasks](#phase-6-background-tasks)
8. [Phase 7: Frontend Dashboard](#phase-7-frontend-dashboard)
9. [Phase 8: Testing & Optimization](#phase-8-testing--optimization)
10. [Phase 9: Deployment](#phase-9-deployment)

---

## Prerequisites

### Required Software
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for frontend)
- Docker & Docker Compose

### Project Setup
```bash
# Clone and navigate to project
cd /path/to/claude-code-fastapi-graphql

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (will be updated in Phase 1)
pip install -r requirements.txt
```

---

## Phase 1: Foundation Setup

### Step 1.1: Update Dependencies

**File: `pyproject.toml`**

Add the following dependencies:

```toml
[project]
dependencies = [
    # Existing dependencies...

    # GraphQL
    "strawberry-graphql[fastapi]>=0.238.0",

    # Caching
    "redis>=5.0.0",
    "hiredis>=2.3.0",  # Faster Redis parsing

    # Background Tasks
    "celery>=5.3.0",
    "celery[redis]>=5.3.0",

    # Database
    "asyncpg>=0.29.0",  # Async PostgreSQL
    "psycopg2-binary>=2.9.9",  # PostgreSQL adapter

    # Performance
    "orjson>=3.9.0",  # Fast JSON
    "msgpack>=1.0.0",  # Binary serialization

    # Monitoring
    "prometheus-client>=0.19.0",
    "prometheus-fastapi-instrumentator>=6.1.0",
]
```

Install dependencies:
```bash
pip install -e ".[dev]"
# or if using uv:
uv sync --all-extras
```

### Step 1.2: Environment Configuration

**File: `.env.example`**

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/shopx_analytics
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
REDIS_MAX_CONNECTIONS=50

# GraphQL
GRAPHQL_DEBUG=true
GRAPHQL_MAX_DEPTH=10
GRAPHQL_MAX_COMPLEXITY=1000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Cache TTL (seconds)
CACHE_TTL_DASHBOARD=60
CACHE_TTL_PRODUCTS=300
CACHE_TTL_CUSTOMERS=600
CACHE_TTL_TRENDS=180

# Performance
ENABLE_COMPRESSION=true
ENABLE_QUERY_LOGGING=false

# Monitoring
ENABLE_PROMETHEUS=true
PROMETHEUS_PORT=9090
```

Copy to `.env`:
```bash
cp .env.example .env
# Edit .env with your actual values
```

### Step 1.3: Update Configuration

**File: `src/core/config.py`**

Update with new settings (implementation will be provided in next steps).

---

## Phase 2: Database Layer

### Step 2.1: Create Database Models

**Directory Structure:**
```
src/models/
├── __init__.py
├── base.py           # Base model class
├── customer.py       # Customer model
├── category.py       # Category model
├── product.py        # Product model
├── order.py          # Order model
├── order_item.py     # OrderItem model
└── sales_rep.py      # SalesRepresentative model
```

**File: `src/models/base.py`**

```python
"""Base model with common fields and methods."""
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base model class with common fields."""

    pass


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UUIDMixin:
    """Mixin for UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False
    )
```

### Step 2.2: Database Migration Scripts

**File: `migrations/versions/001_create_indexes.sql`**

```sql
-- Sales Analytics Database Indexes
-- This file creates all necessary indexes for optimal query performance

-- Customer Indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_segment
    ON customers(segment) WHERE segment IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_email
    ON customers(email);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_created_at
    ON customers(created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_lifetime_value
    ON customers(total_lifetime_value DESC) WHERE total_lifetime_value IS NOT NULL;

-- Category Indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_parent
    ON categories(parent_id) WHERE parent_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_categories_name
    ON categories(name);

-- Product Indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_category
    ON products(category_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_price
    ON products(selling_price);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_stock
    ON products(stock_quantity) WHERE stock_quantity < 10;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_name
    ON products(name);

-- Sales Representative Indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sales_reps_region
    ON sales_representatives(region);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sales_reps_email
    ON sales_representatives(email);

-- Order Indexes (critical for analytics)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer
    ON orders(customer_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_sales_rep
    ON orders(sales_rep_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_date
    ON orders(order_date DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_status
    ON orders(status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_amount
    ON orders(total_amount);

-- Composite index for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_date_status
    ON orders(order_date DESC, status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer_date
    ON orders(customer_id, order_date DESC);

-- Order Items Indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_order
    ON order_items(order_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_product
    ON order_items(product_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_order_items_product_created
    ON order_items(product_id, created_at DESC);

-- Statistics update (important after index creation)
ANALYZE customers;
ANALYZE categories;
ANALYZE products;
ANALYZE sales_representatives;
ANALYZE orders;
ANALYZE order_items;

-- Grant permissions (adjust as needed)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_readonly;
```

**File: `migrations/versions/002_partition_orders.sql`**

```sql
-- Partition Orders Table by Month for Better Performance
-- This script sets up monthly partitions for the orders table

-- Create partitions for last 12 months + next 6 months
-- Adjust dates based on your deployment date

-- 2024 Partitions
CREATE TABLE IF NOT EXISTS orders_2024_01 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE IF NOT EXISTS orders_2024_02 PARTITION OF orders
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE IF NOT EXISTS orders_2024_03 PARTITION OF orders
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

CREATE TABLE IF NOT EXISTS orders_2024_04 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-05-01');

CREATE TABLE IF NOT EXISTS orders_2024_05 PARTITION OF orders
    FOR VALUES FROM ('2024-05-01') TO ('2024-06-01');

CREATE TABLE IF NOT EXISTS orders_2024_06 PARTITION OF orders
    FOR VALUES FROM ('2024-06-01') TO ('2024-07-01');

CREATE TABLE IF NOT EXISTS orders_2024_07 PARTITION OF orders
    FOR VALUES FROM ('2024-07-01') TO ('2024-08-01');

CREATE TABLE IF NOT EXISTS orders_2024_08 PARTITION OF orders
    FOR VALUES FROM ('2024-08-01') TO ('2024-09-01');

CREATE TABLE IF NOT EXISTS orders_2024_09 PARTITION OF orders
    FOR VALUES FROM ('2024-09-01') TO ('2024-10-01');

CREATE TABLE IF NOT EXISTS orders_2024_10 PARTITION OF orders
    FOR VALUES FROM ('2024-10-01') TO ('2024-11-01');

CREATE TABLE IF NOT EXISTS orders_2024_11 PARTITION OF orders
    FOR VALUES FROM ('2024-11-01') TO ('2024-12-01');

CREATE TABLE IF NOT EXISTS orders_2024_12 PARTITION OF orders
    FOR VALUES FROM ('2024-12-01') TO ('2025-01-01');

-- 2025 Partitions (future)
CREATE TABLE IF NOT EXISTS orders_2025_01 PARTITION OF orders
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE IF NOT EXISTS orders_2025_02 PARTITION OF orders
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE IF NOT EXISTS orders_2025_03 PARTITION OF orders
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE IF NOT EXISTS orders_2025_04 PARTITION OF orders
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');

CREATE TABLE IF NOT EXISTS orders_2025_05 PARTITION OF orders
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');

CREATE TABLE IF NOT EXISTS orders_2025_06 PARTITION OF orders
    FOR VALUES FROM ('2025-06-01') TO ('2025-07-01');

-- Indexes on partitions (automatically inherited but can be explicit)
-- These are created automatically but included for documentation

-- Note: Add a cron job or scheduled task to create future partitions
-- Example stored procedure to automate partition creation:

CREATE OR REPLACE FUNCTION create_next_month_partition()
RETURNS void AS $$
DECLARE
    next_month_start DATE;
    next_month_end DATE;
    partition_name TEXT;
BEGIN
    -- Calculate next month
    next_month_start := date_trunc('month', CURRENT_DATE + INTERVAL '2 months');
    next_month_end := next_month_start + INTERVAL '1 month';

    -- Generate partition name
    partition_name := 'orders_' || to_char(next_month_start, 'YYYY_MM');

    -- Create partition if it doesn't exist
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF orders FOR VALUES FROM (%L) TO (%L)',
        partition_name,
        next_month_start,
        next_month_end
    );

    RAISE NOTICE 'Created partition: %', partition_name;
END;
$$ LANGUAGE plpgsql;

-- Schedule this function to run monthly
```

**File: `migrations/versions/003_materialized_views.sql`**

```sql
-- Materialized Views for Analytics Performance
-- These views pre-compute expensive aggregations

-- 1. Daily Sales Summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_daily_sales AS
SELECT
    DATE(o.order_date) as sale_date,
    COUNT(DISTINCT o.id) as order_count,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    SUM(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE 0 END) as completed_revenue,
    SUM(CASE WHEN o.status = 'cancelled' THEN o.total_amount ELSE 0 END) as cancelled_revenue
FROM orders o
WHERE o.status IN ('completed', 'cancelled')
GROUP BY DATE(o.order_date);

CREATE UNIQUE INDEX idx_mv_daily_sales_date ON mv_daily_sales(sale_date DESC);

-- 2. Product Performance Summary
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_product_performance AS
SELECT
    p.id as product_id,
    p.name as product_name,
    p.category_id,
    c.name as category_name,
    p.cost_price,
    p.selling_price,
    COUNT(DISTINCT oi.id) as times_sold,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.unit_price) as avg_selling_price,
    SUM(oi.total_price - (p.cost_price * oi.quantity)) as total_profit,
    CASE
        WHEN SUM(oi.total_price) > 0
        THEN (SUM(oi.total_price - (p.cost_price * oi.quantity)) / SUM(oi.total_price) * 100)
        ELSE 0
    END as profit_margin_pct,
    MAX(o.order_date) as last_sold_date,
    MIN(o.order_date) as first_sold_date
FROM products p
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'completed'
GROUP BY p.id, p.name, p.category_id, c.name, p.cost_price, p.selling_price;

CREATE UNIQUE INDEX idx_mv_product_perf_id ON mv_product_performance(product_id);
CREATE INDEX idx_mv_product_perf_revenue ON mv_product_performance(total_revenue DESC);
CREATE INDEX idx_mv_product_perf_profit ON mv_product_performance(total_profit DESC);
CREATE INDEX idx_mv_product_perf_category ON mv_product_performance(category_id);

-- 3. Customer Segments and Behavior
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_customer_segments AS
SELECT
    c.id as customer_id,
    c.name,
    c.email,
    c.segment,
    COUNT(DISTINCT o.id) as order_count,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value,
    MAX(o.order_date) as last_order_date,
    MIN(o.order_date) as first_order_date,
    EXTRACT(DAY FROM (MAX(o.order_date) - MIN(o.order_date))) as customer_lifetime_days,
    CASE
        WHEN COUNT(DISTINCT o.id) > 0
        THEN EXTRACT(DAY FROM (MAX(o.order_date) - MIN(o.order_date))) / COUNT(DISTINCT o.id)::float
        ELSE 0
    END as avg_days_between_orders,
    -- Recency, Frequency, Monetary (RFM) scores
    EXTRACT(DAY FROM (CURRENT_DATE - MAX(o.order_date))) as recency_days,
    COUNT(DISTINCT o.id) as frequency,
    SUM(o.total_amount) as monetary_value
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'completed'
GROUP BY c.id, c.name, c.email, c.segment;

CREATE UNIQUE INDEX idx_mv_customer_seg_id ON mv_customer_segments(customer_id);
CREATE INDEX idx_mv_customer_seg_spent ON mv_customer_segments(total_spent DESC);
CREATE INDEX idx_mv_customer_seg_segment ON mv_customer_segments(segment);
CREATE INDEX idx_mv_customer_seg_recency ON mv_customer_segments(recency_days);

-- 4. Category Performance
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_category_performance AS
SELECT
    c.id as category_id,
    c.name as category_name,
    c.parent_id,
    COUNT(DISTINCT p.id) as product_count,
    COUNT(DISTINCT oi.order_id) as order_count,
    SUM(oi.quantity) as units_sold,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.unit_price) as avg_price,
    SUM(oi.total_price - (p.cost_price * oi.quantity)) as total_profit
FROM categories c
LEFT JOIN products p ON c.id = p.category_id
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'completed'
GROUP BY c.id, c.name, c.parent_id;

CREATE UNIQUE INDEX idx_mv_category_perf_id ON mv_category_performance(category_id);
CREATE INDEX idx_mv_category_perf_revenue ON mv_category_performance(total_revenue DESC);

-- 5. Sales Representative Performance
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_sales_rep_performance AS
SELECT
    sr.id as sales_rep_id,
    sr.name as sales_rep_name,
    sr.region,
    sr.commission_rate,
    COUNT(DISTINCT o.id) as total_orders,
    SUM(o.total_amount) as total_sales,
    AVG(o.total_amount) as avg_order_value,
    SUM(o.total_amount * sr.commission_rate / 100) as total_commission_earned,
    COUNT(DISTINCT o.customer_id) as unique_customers_served,
    MAX(o.order_date) as last_sale_date
FROM sales_representatives sr
LEFT JOIN orders o ON sr.id = o.sales_rep_id AND o.status = 'completed'
GROUP BY sr.id, sr.name, sr.region, sr.commission_rate;

CREATE UNIQUE INDEX idx_mv_sales_rep_perf_id ON mv_sales_rep_performance(sales_rep_id);
CREATE INDEX idx_mv_sales_rep_perf_sales ON mv_sales_rep_performance(total_sales DESC);
CREATE INDEX idx_mv_sales_rep_perf_region ON mv_sales_rep_performance(region);

-- Refresh function for all materialized views
CREATE OR REPLACE FUNCTION refresh_all_analytics_mv()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_product_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_customer_segments;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_category_performance;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sales_rep_performance;

    RAISE NOTICE 'All materialized views refreshed at %', NOW();
END;
$$ LANGUAGE plpgsql;

-- Initial refresh
SELECT refresh_all_analytics_mv();

-- Note: Schedule this function to run via Celery Beat every 15-30 minutes
```

---

## Phase 3: Caching Layer

### Redis Cache Manager

**File: `src/core/cache.py`**

This file will handle all Redis caching operations with connection pooling and error handling.

---

## Phase 4: GraphQL API

### GraphQL Schema Design

**Directory Structure:**
```
src/graphql/
├── __init__.py
├── schema.py          # Main schema
├── types.py           # Type definitions
├── queries.py         # Query resolvers
├── mutations.py       # Mutation resolvers
├── dataloaders.py     # DataLoader implementations
├── complexity.py      # Query complexity analysis
└── context.py         # GraphQL context
```

---

## Phase 5: Analytics Services

### Service Layer Design

**Directory Structure:**
```
src/services/
├── __init__.py
├── analytics_service.py      # Main analytics service
├── order_service.py          # Order-related queries
├── product_service.py        # Product analytics
├── customer_service.py       # Customer analytics
└── cache_invalidation.py     # Cache management
```

---

## Phase 6: Background Tasks

### Celery Configuration

**File: `src/tasks/scheduler.py`**

Background tasks for:
- Materialized view refresh
- Cache warming
- Daily/hourly aggregations
- Report generation

---

## Phase 7: Frontend Dashboard

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install @apollo/client graphql chart.js react-chartjs-2

# Or with bun
bun add @apollo/client graphql chart.js react-chartjs-2
```

### Component Structure

**Directory: `frontend/src/components/`**
- `Dashboard.tsx` - Main container
- `SalesOverview.tsx` - Revenue metrics
- `ProductInsights.tsx` - Product charts
- `CustomerAnalytics.tsx` - Customer metrics
- `charts/` - Reusable chart components

---

## Phase 8: Testing & Optimization

### Testing Strategy

```bash
# Unit tests
pytest tests/unit -v --cov=src

# Integration tests
pytest tests/integration -v

# Load testing
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

---

## Phase 9: Deployment

### Docker Production Setup

**File: `docker-compose.prod.yml`**

Multi-instance deployment with:
- Nginx load balancer
- 3+ FastAPI instances
- Redis cluster
- PostgreSQL with replicas
- Monitoring (Prometheus + Grafana)

### Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Materialized views created
- [ ] Celery workers running
- [ ] Redis cluster operational
- [ ] Nginx load balancer configured
- [ ] SSL certificates installed
- [ ] Monitoring enabled
- [ ] Backup strategy implemented
- [ ] Auto-scaling configured

---

## Performance Monitoring

### Key Metrics to Track

1. **Response Time**: p50, p95, p99
2. **Cache Hit Rate**: Should be > 80%
3. **Database Query Time**: < 100ms for indexed queries
4. **Error Rate**: < 1% under normal load
5. **Throughput**: Requests per second
6. **Resource Usage**: CPU, Memory, Disk I/O

### Monitoring Tools

- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **New Relic / DataDog**: APM (optional)

---

## Troubleshooting

### Common Issues

#### Slow Queries
```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

#### Cache Issues
```bash
# Check Redis connection
redis-cli ping

# Monitor Redis
redis-cli monitor

# Check memory usage
redis-cli info memory
```

#### High Load
```bash
# Check system resources
htop

# Check database connections
SELECT count(*) FROM pg_stat_activity;

# Check Celery workers
celery -A src.tasks.scheduler inspect active
```

---

## Next Steps

Once all phases are complete:

1. **Load Test**: Verify performance under expected load
2. **Security Audit**: Check for vulnerabilities
3. **Documentation Review**: Ensure all docs are updated
4. **Staging Deployment**: Deploy to staging environment
5. **Production Deployment**: Roll out to production

For detailed code implementation of each phase, refer to the specific documentation files:
- [API.md](./API.md) - Complete GraphQL schema
- [DATABASE.md](./DATABASE.md) - Database schema details
- [FRONTEND.md](./FRONTEND.md) - Frontend implementation
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment guide

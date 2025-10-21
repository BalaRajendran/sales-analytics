# Sales Analytics Dashboard - Architecture Documentation

## 🎯 Overview

This document describes the high-performance, scalable architecture for the ShopX Sales Analytics Dashboard. The system is designed to handle huge traffic with sub-second response times through intelligent caching, database optimizations, and efficient GraphQL queries.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer (Nginx)                    │
│                     (Traffic Distribution)                       │
└────────────┬──────────────────┬──────────────────┬──────────────┘
             │                  │                  │
    ┌────────▼────────┐ ┌──────▼────────┐ ┌──────▼────────┐
    │  FastAPI + GraphQL│ │FastAPI + GraphQL│ │FastAPI + GraphQL│
    │    Instance 1    │ │   Instance 2   │ │   Instance 3   │
    └────────┬─────────┘ └──────┬─────────┘ └──────┬─────────┘
             │                  │                  │
             └──────────┬───────┴──────────┬───────┘
                        │                  │
         ┌──────────────▼──────┐  ┌───────▼────────────┐
         │   Redis Cache       │  │  Celery Workers    │
         │   - Query Results   │  │  - Async Tasks     │
         │   - Session Data    │  │  - Cache Refresh   │
         │   - Rate Limiting   │  │  - Aggregations    │
         └──────────────┬──────┘  └───────┬────────────┘
                        │                  │
                        └────────┬─────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   PostgreSQL Database   │
                    │   - OLTP Tables         │
                    │   - Materialized Views  │
                    │   - Aggregation Tables  │
                    │   - Partitioned Orders  │
                    └─────────────────────────┘
```

## 🎯 Key Design Principles

### 1. **Multi-Tier Caching (Highway Lanes)**
Like a highway with multiple lanes for different speeds:

- **Fast Lane (L1)**: Redis cache for hot data (< 10ms)
- **Medium Lane (L2)**: Materialized views (< 100ms)
- **Slow Lane (L3)**: Aggregation tables (< 500ms)
- **Emergency Lane**: Direct database queries (< 2s)

### 2. **Read/Write Separation**
- **OLTP (Write)**: Real-time order processing
- **OLAP (Read)**: Analytics queries on replicas/materialized views

### 3. **Asynchronous Processing**
- Background tasks for heavy computations
- Non-blocking cache refresh
- Scheduled aggregation updates

### 4. **Query Optimization**
- DataLoaders for N+1 prevention
- Query complexity analysis
- Depth limiting
- Batch operations

## 📊 Database Schema

### Core Tables

```sql
-- Customers Table
CREATE TABLE customers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    segment VARCHAR(50), -- 'Premium', 'Regular', 'New'
    total_lifetime_value DECIMAL(15,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Categories Table
CREATE TABLE categories (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES categories(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Products Table
CREATE TABLE products (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id UUID REFERENCES categories(id),
    cost_price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sales Representatives Table
CREATE TABLE sales_representatives (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    region VARCHAR(100),
    commission_rate DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Orders Table (Partitioned by created_at)
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(id),
    sales_rep_id UUID REFERENCES sales_representatives(id),
    order_date TIMESTAMPTZ NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(50), -- 'pending', 'completed', 'cancelled'
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Order Items Table
CREATE TABLE order_items (
    id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(15,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Optimizations

#### 1. **Indexes**
```sql
-- Customer indexes
CREATE INDEX idx_customers_segment ON customers(segment);
CREATE INDEX idx_customers_created_at ON customers(created_at);

-- Product indexes
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(selling_price);

-- Order indexes
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_sales_rep ON orders(sales_rep_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);

-- Order items indexes
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

#### 2. **Partitioning Strategy**
```sql
-- Monthly partitions for orders (last 12 months + future)
CREATE TABLE orders_2024_01 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE orders_2024_02 PARTITION OF orders
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- ... continue for all months
```

#### 3. **Materialized Views**
```sql
-- Daily Sales Summary
CREATE MATERIALIZED VIEW mv_daily_sales AS
SELECT
    DATE(order_date) as sale_date,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM orders
WHERE status = 'completed'
GROUP BY DATE(order_date);

CREATE INDEX idx_mv_daily_sales_date ON mv_daily_sales(sale_date);

-- Product Performance
CREATE MATERIALIZED VIEW mv_product_performance AS
SELECT
    p.id as product_id,
    p.name as product_name,
    p.category_id,
    COUNT(oi.id) as times_sold,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.total_price) as total_revenue,
    SUM(oi.total_price - (p.cost_price * oi.quantity)) as total_profit
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'completed'
GROUP BY p.id, p.name, p.category_id;

CREATE INDEX idx_mv_product_perf_revenue ON mv_product_performance(total_revenue DESC);

-- Customer Segments
CREATE MATERIALIZED VIEW mv_customer_segments AS
SELECT
    c.id as customer_id,
    c.name,
    c.segment,
    COUNT(o.id) as order_count,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value,
    MAX(o.order_date) as last_order_date,
    MIN(o.order_date) as first_order_date
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id AND o.status = 'completed'
GROUP BY c.id, c.name, c.segment;
```

#### 4. **Aggregation Tables**
```sql
-- Pre-computed hourly metrics
CREATE TABLE agg_hourly_metrics (
    metric_hour TIMESTAMPTZ PRIMARY KEY,
    revenue DECIMAL(15,2),
    order_count INTEGER,
    avg_order_value DECIMAL(10,2),
    unique_customers INTEGER,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pre-computed category performance
CREATE TABLE agg_category_performance (
    category_id UUID PRIMARY KEY,
    period VARCHAR(20), -- 'today', 'week', 'month', 'year'
    revenue DECIMAL(15,2),
    profit DECIMAL(15,2),
    units_sold INTEGER,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔄 Caching Strategy

### Cache Layers

#### Layer 1: Redis Cache (Hot Data)
```python
# TTL Strategy
CACHE_TTL = {
    "dashboard_overview": 60,      # 1 minute
    "product_insights": 300,       # 5 minutes
    "customer_analytics": 600,     # 10 minutes
    "sales_trends": 180,           # 3 minutes
    "realtime_metrics": 30,        # 30 seconds
}

# Cache Keys Pattern
CACHE_KEYS = {
    "overview": "analytics:overview:{date_range}",
    "product": "analytics:product:{product_id}:{period}",
    "customer": "analytics:customer:{customer_id}",
    "trend": "analytics:trend:{metric}:{period}",
}
```

#### Layer 2: Materialized Views
- Refreshed every 15-30 minutes via Celery
- Used for complex aggregations
- Indexed for fast access

#### Layer 3: Application-Level Caching
- Python `@lru_cache` for function results
- In-memory caching for configuration

### Cache Invalidation Strategy

```python
# Event-driven invalidation
INVALIDATION_RULES = {
    "order_created": ["dashboard_overview", "sales_trends", "realtime_metrics"],
    "order_updated": ["dashboard_overview", "sales_trends"],
    "product_updated": ["product_insights", "dashboard_overview"],
    "customer_updated": ["customer_analytics"],
}

# Time-based invalidation
- Scheduled refresh via Celery Beat
- Background updates during low-traffic periods
```

## 🔌 GraphQL API Design

### Schema Structure

```graphql
type Query {
  # Sales Overview
  salesOverview(dateRange: DateRangeInput!): SalesOverview!
  salesTrends(period: Period!, metric: Metric!): [TrendPoint!]!

  # Product Insights
  topProducts(limit: Int = 10, sortBy: ProductSort!): [ProductInsight!]!
  productPerformance(productId: ID!, period: Period!): ProductPerformance!
  categoryBreakdown(period: Period!): [CategoryInsight!]!

  # Customer Analytics
  customerSegments: [CustomerSegment!]!
  customerLifetimeValue(customerId: ID!): CustomerLTV!
  customerRetention(period: Period!): RetentionMetrics!

  # Profitability
  profitabilityMetrics(period: Period!): ProfitabilityMetrics!
  marginAnalysis(groupBy: GroupBy!): [MarginAnalysis!]!
}

type SalesOverview {
  totalRevenue: Float!
  totalOrders: Int!
  averageOrderValue: Float!
  growthRate: Float!
  revenueChange: Float!
  orderChange: Float!
}

type TrendPoint {
  timestamp: DateTime!
  value: Float!
  label: String!
}

type ProductInsight {
  product: Product!
  revenue: Float!
  unitsSold: Int!
  profit: Float!
  profitMargin: Float!
  growthRate: Float!
}

input DateRangeInput {
  startDate: DateTime!
  endDate: DateTime!
}

enum Period {
  TODAY
  WEEK
  MONTH
  QUARTER
  YEAR
  CUSTOM
}

enum Metric {
  REVENUE
  ORDERS
  CUSTOMERS
  AOV
}
```

### Query Optimization Techniques

#### 1. **DataLoaders (N+1 Prevention)**
```python
# Batch load products for order items
async def load_products(product_ids: List[str]) -> List[Product]:
    # Single query instead of N queries
    products = await db.query(Product).filter(Product.id.in_(product_ids)).all()
    return products

# Usage in resolver
product_loader = DataLoader(load_products)
```

#### 2. **Query Complexity Analysis**
```python
MAX_COMPLEXITY = 1000
COMPLEXITY_WEIGHTS = {
    "salesOverview": 10,
    "topProducts": 20,
    "customerSegments": 50,
    "salesTrends": 30,
}
```

#### 3. **Field-Level Caching**
```python
@strawberry.field
@cached(ttl=300, key="product:{self.id}")
async def performance(self, period: Period) -> ProductPerformance:
    return await calculate_performance(self.id, period)
```

## 🎨 Frontend Architecture

### Technology Stack
- **Apollo Client** for GraphQL
- **Chart.js / Recharts** for visualizations
- **React Query** for additional caching
- **TanStack Virtual** for large lists

### Component Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard.tsx          # Main dashboard container
│   │   ├── SalesOverview.tsx      # Sales metrics cards
│   │   ├── ProductInsights.tsx    # Product charts
│   │   ├── CustomerAnalytics.tsx  # Customer metrics
│   │   └── charts/
│   │       ├── LineChart.tsx
│   │       ├── BarChart.tsx
│   │       ├── PieChart.tsx
│   │       └── AreaChart.tsx
│   ├── graphql/
│   │   ├── queries.ts             # GraphQL queries
│   │   └── fragments.ts           # Reusable fragments
│   ├── lib/
│   │   ├── apollo-client.ts       # Apollo setup
│   │   └── chart-config.ts        # Chart defaults
│   └── hooks/
│       ├── useAnalytics.ts        # Custom hooks
│       └── useChartData.ts
```

### Data Fetching Strategy
```typescript
// Smart caching with Apollo
const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        salesOverview: {
          merge: true,
          read(existing, { args }) {
            // Return cached if fresh
            if (existing && isFresh(existing, args)) {
              return existing;
            }
          }
        }
      }
    }
  }
});

// Polling for real-time updates
const { data } = useQuery(SALES_OVERVIEW_QUERY, {
  pollInterval: 60000, // 1 minute
  fetchPolicy: 'cache-and-network'
});
```

## 🚀 Performance Optimization

### Backend Optimizations

#### 1. **Connection Pooling**
```python
# PostgreSQL connection pool
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 3600,
}
```

#### 2. **Query Optimization**
```python
# Use select_related and prefetch_related
orders = await db.query(Order)\
    .options(
        selectinload(Order.items).selectinload(OrderItem.product),
        selectinload(Order.customer)
    )\
    .all()
```

#### 3. **Response Compression**
```python
# Gzip compression for responses > 1KB
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
    compresslevel=6
)
```

#### 4. **Async Operations**
```python
# All I/O operations are async
async def get_sales_overview(date_range: DateRange) -> SalesOverview:
    # Check cache first
    cached = await redis.get(cache_key)
    if cached:
        return cached

    # Parallel queries
    revenue, orders, customers = await asyncio.gather(
        get_total_revenue(date_range),
        get_order_count(date_range),
        get_unique_customers(date_range)
    )

    result = SalesOverview(revenue, orders, customers)
    await redis.setex(cache_key, 60, result)
    return result
```

### Frontend Optimizations

#### 1. **Code Splitting**
```typescript
const ProductInsights = lazy(() => import('./components/ProductInsights'));
const CustomerAnalytics = lazy(() => import('./components/CustomerAnalytics'));
```

#### 2. **Virtual Scrolling**
```typescript
// For large product lists
import { useVirtual } from '@tanstack/react-virtual';
```

#### 3. **Memoization**
```typescript
const chartData = useMemo(() => {
  return transformDataForChart(data);
}, [data]);
```

## 📈 Scalability Considerations

### Horizontal Scaling
- **Stateless application servers** (scale to 10+ instances)
- **Load balancing** with Nginx/HAProxy
- **Session storage** in Redis
- **Shared cache** across instances

### Database Scaling
- **Read replicas** for analytics queries
- **Partitioning** for time-series data
- **Archiving** old data (> 2 years)
- **Sharding** by customer/region (future)

### Monitoring & Observability
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

graphql_requests = Counter(
    'graphql_requests_total',
    'Total GraphQL requests',
    ['operation', 'status']
)

graphql_duration = Histogram(
    'graphql_request_duration_seconds',
    'GraphQL request duration'
)
```

## 🔒 Security

### API Security
- **Rate limiting**: 100 requests/minute per IP
- **Query depth limiting**: Max depth of 10
- **Query complexity**: Max complexity of 1000
- **Authentication**: JWT tokens
- **Authorization**: Role-based access control

### Database Security
- **Connection encryption** (SSL/TLS)
- **Parameter binding** (SQL injection prevention)
- **Read-only users** for analytics
- **Audit logging** for sensitive operations

## 📊 Performance Targets

### Response Time SLAs
- **Dashboard Overview**: < 200ms (p95)
- **Product Insights**: < 300ms (p95)
- **Customer Analytics**: < 400ms (p95)
- **Trend Charts**: < 250ms (p95)

### Throughput
- **1,000 req/sec** per instance
- **10,000+ concurrent users** with 10 instances
- **< 1% error rate** under normal load
- **< 5% error rate** under 2x peak load

### Cache Performance
- **Cache hit rate**: > 80%
- **Cache response time**: < 10ms
- **Redis memory**: < 2GB for 1M records

## 🛠️ Development Workflow

### Local Development
```bash
# Start services
docker-compose up -d postgres redis

# Run migrations
make migrate

# Seed data
python scripts/seed_data.py --records 100000

# Start backend
make dev

# Start frontend
cd frontend && npm run dev
```

### Testing Strategy
```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Performance tests
locust -f tests/performance/locustfile.py
```

## 📚 Additional Documentation

- [API Documentation](./API.md) - GraphQL schema and queries
- [Database Schema](./DATABASE.md) - Complete schema reference
- [Deployment Guide](./DEPLOYMENT.md) - Production deployment
- [Performance Tuning](./PERFORMANCE.md) - Optimization tips
- [Frontend Guide](./FRONTEND.md) - Component library

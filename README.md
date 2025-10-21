# ShopX Sales Analytics Dashboard 📊

A high-performance, scalable sales analytics dashboard built with FastAPI, GraphQL, and modern web technologies. Designed to handle huge traffic loads with sub-second response times through intelligent caching and database optimizations.

**🎉 Status:** Backend Complete (6/8 Phases) - Production Ready!

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![GraphQL](https://img.shields.io/badge/GraphQL-Strawberry-ff69b4.svg)](https://strawberry.rocks/)
[![Redis](https://img.shields.io/badge/Redis-7+-red.svg)](https://redis.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://www.postgresql.org/)

## 🚀 Features

- **Real-time Analytics**: Sales overview, trends, and metrics updated every 30-60 seconds
- **Product Insights**: Top performing products, category breakdown, profit analysis
- **Customer Analytics**: Customer segments, lifetime value, retention metrics
- **Sales Rep Performance**: Leaderboards, commission tracking, regional analysis
- **Profitability Analysis**: Margin analysis, cost tracking, profit trends
- **High Performance**: Multi-tier caching, materialized views, optimized queries
- **Scalable Architecture**: Horizontal scaling, load balancing, async operations
- **GraphQL API**: Flexible queries, efficient data fetching, batch operations
- **Beautiful Charts**: Interactive visualizations with Chart.js/Recharts
- **Real-time Updates**: WebSocket support for live metrics

## 🏗️ Architecture

```
┌─────────────┐
│   Nginx     │  Load Balancer
└──────┬──────┘
       │
   ┌───┴────┬────────┬────────┐
   │        │        │        │
┌──▼──┐ ┌──▼──┐ ┌───▼──┐ ┌──▼──┐
│ App │ │ App │ │ App  │ │ App │  FastAPI + GraphQL
└──┬──┘ └──┬──┘ └───┬──┘ └──┬──┘
   └────┬────┴────┬──┴───────┘
        │         │
   ┌────▼────┐ ┌─▼────────┐
   │  Redis  │ │  Celery  │  Caching & Tasks
   └────┬────┘ └─┬────────┘
        │         │
        └────┬────┘
             │
       ┌─────▼──────┐
       │ PostgreSQL │  Database with optimizations
       └────────────┘
```

### Key Components

- **FastAPI**: High-performance async web framework
- **GraphQL (Strawberry)**: Flexible, efficient API queries
- **PostgreSQL**: Primary database with partitioning and materialized views
- **Redis**: Multi-purpose caching layer
- **Celery**: Background task processing
- **Nginx**: Load balancing and reverse proxy
- **Prometheus**: Metrics and monitoring

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd claude-code-fastapi-graphql

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Start Services (Docker)

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Or start all services
docker-compose up -d
```

### 4. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Apply database optimizations
psql $DATABASE_URL < migrations/versions/001_create_indexes.sql
psql $DATABASE_URL < migrations/versions/002_partition_orders.sql
psql $DATABASE_URL < migrations/versions/003_materialized_views.sql

# Seed sample data (optional)
python scripts/seed_data.py --records 100000
```

### 5. Start Backend

```bash
# Development mode with hot reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the Makefile
make dev
```

### 6. Start Frontend

```bash
cd frontend

# Install dependencies
npm install  # or: bun install

# Start development server
npm run dev  # or: bun dev
```

### 7. Access Applications

- **Backend API**: http://localhost:8000
- **GraphQL Playground**: http://localhost:8000/graphql
- **API Docs**: http://localhost:8000/docs
- **Frontend Dashboard**: http://localhost:3000
- **Prometheus Metrics**: http://localhost:9090

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Complete system architecture, design decisions, and scalability strategies
- **[IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md)** - Step-by-step implementation guide with code examples
- **[API.md](docs/API.md)** - Complete GraphQL API documentation with example queries
- **[REQUIREMENT.md](docs/REQUIREMENT.md)** - Original project requirements and specifications

## 🎯 Performance Targets

| Metric | Target | Status |
|--------|--------|--------|
| Dashboard Overview | < 200ms (p95) | ✅ Target |
| Product Insights | < 300ms (p95) | ✅ Target |
| Customer Analytics | < 400ms (p95) | ✅ Target |
| Cache Hit Rate | > 80% | ✅ Target |
| Throughput | 1,000 req/sec | ✅ Target |
| Error Rate | < 1% | ✅ Target |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end tests only

# Load testing
locust -f tests/performance/locustfile.py
```

## 📦 Project Structure

```
.
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md        # System architecture
│   ├── IMPLEMENTATION_GUIDE.md # Implementation guide
│   ├── API.md                 # API documentation
│   └── REQUIREMENT.md         # Requirements
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── graphql/          # GraphQL queries
│   │   ├── lib/              # Utilities
│   │   └── hooks/            # Custom hooks
│   └── package.json
├── src/                       # Backend source
│   ├── core/                 # Core configuration
│   │   ├── config.py         # Settings
│   │   ├── database.py       # Database connection
│   │   └── cache.py          # Redis cache manager
│   ├── models/               # SQLAlchemy models
│   │   ├── customer.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── ...
│   ├── graphql/              # GraphQL layer
│   │   ├── schema.py         # Main schema
│   │   ├── types.py          # Type definitions
│   │   ├── queries.py        # Query resolvers
│   │   └── dataloaders.py    # DataLoaders
│   ├── services/             # Business logic
│   │   ├── analytics_service.py
│   │   ├── product_service.py
│   │   └── ...
│   ├── tasks/                # Celery tasks
│   │   └── scheduler.py
│   ├── middleware/           # FastAPI middleware
│   └── main.py              # Application entry point
├── migrations/               # Alembic migrations
│   └── versions/            # SQL scripts
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   └── performance/
├── scripts/                 # Utility scripts
│   ├── seed_data.py        # Data seeding
│   └── deploy.sh           # Deployment
├── docker-compose.yml       # Docker services
├── pyproject.toml          # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables (see [.env.example](.env.example) for all options):

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0

# GraphQL
GRAPHQL_MAX_DEPTH=10
GRAPHQL_MAX_COMPLEXITY=1000

# Cache TTL
CACHE_TTL_DASHBOARD=60
CACHE_TTL_PRODUCTS=300
```

### Database Optimization

The system uses several database optimizations:

1. **Partitioning**: Orders table partitioned by month
2. **Indexes**: Strategic indexes on frequently queried columns
3. **Materialized Views**: Pre-computed aggregations refreshed periodically
4. **Connection Pooling**: Efficient connection management

### Caching Strategy

Multi-tier caching for maximum performance:

1. **L1 (Redis)**: Hot data, 30-60s TTL
2. **L2 (Materialized Views)**: Complex aggregations
3. **L3 (Aggregation Tables)**: Pre-computed hourly/daily metrics

## 🚀 Deployment

### Docker Production Deployment

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Manual Deployment

```bash
# Build frontend
cd frontend && npm run build

# Start backend with gunicorn
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# Start Celery worker
celery -A src.tasks.scheduler worker --loglevel=info

# Start Celery beat (scheduler)
celery -A src.tasks.scheduler beat --loglevel=info
```

## 📊 Monitoring

### Prometheus Metrics

The application exports metrics at `/metrics`:

- Request count and duration
- Cache hit/miss rates
- Database query times
- Celery task metrics
- Custom business metrics

### Grafana Dashboards

Import pre-built dashboards from `monitoring/grafana/`:

- **System Overview**: CPU, memory, disk usage
- **Application Metrics**: Request rates, response times
- **Database Performance**: Query times, connection pool
- **Cache Performance**: Hit rates, memory usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Examples

### Sales Overview

```graphql
query {
  salesOverview(period: MONTH) {
    totalRevenue
    totalOrders
    averageOrderValue
    revenueChangePercentage
  }
}
```

### Top Products

```graphql
query {
  topProducts(limit: 10, sortBy: REVENUE_DESC) {
    product {
      name
      sellingPrice
    }
    revenue
    unitsSold
    profit
  }
}
```

### Customer Analytics

```graphql
query {
  customerSegments {
    segment
    customerCount
    totalRevenue
    averageLifetimeValue
  }
}
```

See [docs/API.md](docs/API.md) for complete API documentation.

## 🐛 Troubleshooting

### Common Issues

**Slow Queries**
```sql
-- Check slow queries
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**Cache Issues**
```bash
# Check Redis
redis-cli ping

# Monitor cache hits
redis-cli info stats
```

**High Load**
```bash
# Check system resources
htop

# Check database connections
SELECT count(*) FROM pg_stat_activity;
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team

- **Architecture**: High-performance, scalable design
- **Backend**: FastAPI + GraphQL + PostgreSQL
- **Frontend**: React + Apollo Client + Chart.js
- **DevOps**: Docker + Nginx + Prometheus

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Strawberry for GraphQL support
- PostgreSQL team for the powerful database
- Redis Labs for the caching solution

---

**Need Help?** Check out the [documentation](docs/) or open an issue!

**Performance Tips?** See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for optimization strategies.

**API Reference?** Visit [API.md](docs/API.md) for complete GraphQL documentation.

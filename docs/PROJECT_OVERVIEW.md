# ShopX Sales Analytics Dashboard - Project Overview

## 🎯 What We're Building

A **high-performance sales analytics dashboard** that handles huge traffic like a highway - with multiple lanes for different speeds (multi-tier caching).

### Key Features
- Real-time sales analytics
- Product performance insights
- Customer segmentation & LTV
- Sales rep leaderboards
- Profitability analysis

### Performance Goals
- ⚡ < 200ms response time (95th percentile)
- 📈 1,000+ requests/second per instance
- 🎯 80%+ cache hit rate
- 🚀 Horizontal scalability

---

## 📁 Project Structure

```
claude-code-fastapi-graphql/
│
├── 📚 docs/                           # ALL DOCUMENTATION HERE
│   ├── README.md                      # Documentation index (START HERE!)
│   │
│   ├── 🎯 Core Documents (Read in this order)
│   ├── REQUIREMENT.md                 # What we're building
│   ├── ARCHITECTURE.md                # How it's designed (MOST IMPORTANT!)
│   ├── IMPLEMENTATION_GUIDE.md        # How to build it step-by-step
│   ├── API.md                         # GraphQL API reference
│   │
│   ├── 🔧 Development Guides
│   ├── development/
│   │   ├── SETUP_GUIDE.md            # Setup dev environment
│   │   └── TESTING_GUIDE.md          # Testing guide
│   │
│   ├── 🚀 Deployment Guides
│   ├── deployment/
│   │   ├── DEPLOYMENT_GUIDE.md       # Production deployment
│   │   └── EC2_DOCKER_DEPLOYMENT.md  # Docker on EC2
│   │
│   └── 📦 Legacy Docs (from template)
│       ├── api/                       # Old REST API docs
│       └── architecture/              # Old architecture
│
├── 💻 src/                            # Backend Source Code
│   ├── core/                          # Configuration & setup
│   │   ├── config.py                 # Settings (updated ✅)
│   │   ├── database.py               # DB connection pool
│   │   └── cache.py                  # Redis cache manager (to create)
│   │
│   ├── models/                        # Database Models (SQLAlchemy)
│   │   ├── customer.py               # Customer model (to create)
│   │   ├── category.py               # Category model (to create)
│   │   ├── product.py                # Product model (to create)
│   │   ├── order.py                  # Order model (to create)
│   │   ├── order_item.py             # OrderItem model (to create)
│   │   └── sales_rep.py              # Sales rep model (to create)
│   │
│   ├── graphql/                       # GraphQL Layer (NEW!)
│   │   ├── schema.py                 # Main GraphQL schema (to create)
│   │   ├── types.py                  # Type definitions (to create)
│   │   ├── queries.py                # Query resolvers (to create)
│   │   ├── mutations.py              # Mutations (to create)
│   │   ├── dataloaders.py            # DataLoaders for N+1 (to create)
│   │   └── complexity.py             # Query complexity analysis (to create)
│   │
│   ├── services/                      # Business Logic
│   │   ├── analytics_service.py      # Main analytics (to create)
│   │   ├── product_service.py        # Product queries (to create)
│   │   ├── customer_service.py       # Customer queries (to create)
│   │   ├── order_service.py          # Order queries (to create)
│   │   └── cache_invalidation.py     # Cache management (to create)
│   │
│   ├── tasks/                         # Background Tasks (Celery)
│   │   └── scheduler.py              # Task scheduler (to create)
│   │
│   ├── middleware/                    # Custom Middleware
│   │   ├── compression.py            # Response compression (to create)
│   │   ├── monitoring.py             # Metrics collection (to create)
│   │   └── security.py               # Security checks (to create)
│   │
│   └── main.py                        # FastAPI app entry point (to update)
│
├── 🗄️ migrations/                     # Database Migrations
│   └── versions/
│       ├── 001_create_indexes.sql    # Index creation (to create)
│       ├── 002_partition_orders.sql  # Table partitioning (to create)
│       ├── 003_materialized_views.sql # Materialized views (to create)
│       └── 004_aggregation_tables.sql # Aggregation tables (to create)
│
├── 🖥️ frontend/                       # React Frontend
│   └── src/
│       ├── components/               # React Components (to create)
│       │   ├── Dashboard.tsx         # Main dashboard
│       │   ├── SalesOverview.tsx     # Sales metrics
│       │   ├── ProductInsights.tsx   # Product charts
│       │   └── CustomerAnalytics.tsx # Customer metrics
│       │
│       ├── graphql/                  # GraphQL Client (to create)
│       │   ├── queries.ts            # GraphQL queries
│       │   └── fragments.ts          # Reusable fragments
│       │
│       └── lib/                      # Utilities (to create)
│           ├── apollo-client.ts      # Apollo Client setup
│           └── chart-config.ts       # Chart.js config
│
├── 🧪 tests/                          # Test Suite
│   ├── unit/                         # Unit tests
│   ├── integration/                  # Integration tests
│   └── performance/                  # Load tests (Locust)
│
├── 🛠️ scripts/                        # Utility Scripts
│   ├── seed_data.py                  # Data seeding (to create)
│   ├── deploy.sh                     # Deployment script (to create)
│   └── health_check.sh               # Health checks (to create)
│
├── ⚙️ Configuration Files
├── pyproject.toml                    # Python dependencies (updated ✅)
├── .env.example                      # Environment template (updated ✅)
├── docker-compose.yml                # Docker services
├── docker-compose.prod.yml           # Production Docker (to create)
├── alembic.ini                       # Alembic config
├── Makefile                          # Dev commands
│
└── 📖 README.md                       # Project overview (updated ✅)
```

---

## 🗺️ Documentation Map

### 1️⃣ **Start Here: [docs/README.md](README.md)**
The main documentation index. Navigate to any doc from here.

### 2️⃣ **Core Documentation (Read in Order)**

| Order | Document | Purpose | Time |
|-------|----------|---------|------|
| 1 | [REQUIREMENT.md](REQUIREMENT.md) | Understand requirements | 15 min |
| 2 | [ARCHITECTURE.md](ARCHITECTURE.md) | Learn system design | 45 min |
| 3 | [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) | Build step-by-step | 2 hrs |
| 4 | [API.md](API.md) | GraphQL API reference | 30 min |

### 3️⃣ **Development Docs**

- [development/SETUP_GUIDE.md](development/SETUP_GUIDE.md) - Environment setup
- [development/TESTING_GUIDE.md](development/TESTING_GUIDE.md) - Testing guide

### 4️⃣ **Deployment Docs**

- [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md) - Production deployment
- [deployment/EC2_DOCKER_DEPLOYMENT.md](deployment/EC2_DOCKER_DEPLOYMENT.md) - Docker on AWS

---

## 📊 Implementation Status

### ✅ Completed
- [x] Documentation structure
- [x] Architecture design
- [x] API specification
- [x] Dependencies updated (pyproject.toml)
- [x] Environment configuration (.env.example)
- [x] Main README

### 🚧 In Progress
- [ ] Database models
- [ ] GraphQL layer
- [ ] Caching layer
- [ ] Services
- [ ] Frontend components

### 📅 Not Started
- [ ] Background tasks (Celery)
- [ ] Testing suite
- [ ] Deployment configuration
- [ ] Monitoring setup

**Overall Progress: 15% Complete**

---

## 🏗️ Architecture at a Glance

### The "Highway" Design

```
┌─────────────────────────────────────────┐
│         Nginx Load Balancer             │
│      (Traffic Distribution)             │
└────────────┬────────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼────┐      ┌────▼────┐
│ FastAPI │ ...  │ FastAPI │  (3+ instances)
│ GraphQL │      │ GraphQL │
└────┬────┘      └────┬────┘
     └───────┬────────┘
             │
    ┌────────▼─────────┐
    │                  │
┌───▼────┐      ┌──────▼─────┐
│ Redis  │      │   Celery   │
│ Cache  │      │  Workers   │
└───┬────┘      └──────┬─────┘
    └────────┬─────────┘
             │
      ┌──────▼──────┐
      │ PostgreSQL  │
      │ + Optimized │
      └─────────────┘
```

### 3-Tier Caching (The "Lanes")

1. **Fast Lane (L1)**: Redis - Hot data, 30-60s TTL
2. **Medium Lane (L2)**: Materialized Views - Complex aggregations
3. **Slow Lane (L3)**: Aggregation Tables - Pre-computed metrics

### Key Technologies

| Layer | Technology | Purpose |
|-------|-----------|----------|
| **API** | FastAPI + Strawberry GraphQL | High-performance async API |
| **Cache** | Redis 7+ | Multi-purpose caching |
| **Database** | PostgreSQL 15+ | Partitioned, optimized |
| **Tasks** | Celery | Background processing |
| **Frontend** | React + Apollo Client | Dashboard UI |
| **Monitoring** | Prometheus + Grafana | Metrics & alerts |

---

## 🚀 Quick Start Commands

```bash
# 1. Setup
pip install -e ".[dev]"
cp .env.example .env

# 2. Start services (Docker)
docker-compose up -d postgres redis

# 3. Run migrations
alembic upgrade head
psql $DATABASE_URL < migrations/versions/001_create_indexes.sql

# 4. Start backend
uvicorn src.main:app --reload

# 5. Start frontend
cd frontend && npm run dev

# 6. Access apps
# Backend: http://localhost:8000
# GraphQL: http://localhost:8000/graphql
# Frontend: http://localhost:3000
```

---

## 📝 Key Files to Know

### Configuration
- [.env.example](.env.example) - Environment variables
- [pyproject.toml](../pyproject.toml) - Python dependencies
- [src/core/config.py](../src/core/config.py) - Settings class

### Database
- [migrations/](../migrations/) - Database migrations
- [src/models/](../src/models/) - SQLAlchemy models

### API
- [src/graphql/](../src/graphql/) - GraphQL schema & resolvers
- [src/services/](../src/services/) - Business logic

### Frontend
- [frontend/src/components/](../frontend/src/components/) - React components
- [frontend/src/graphql/](../frontend/src/graphql/) - GraphQL queries

---

## 🎯 Next Steps

### For Developers

1. **Read the docs** in this order:
   - [REQUIREMENT.md](REQUIREMENT.md) - 15 min
   - [ARCHITECTURE.md](ARCHITECTURE.md) - 45 min
   - [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Browse

2. **Set up environment**:
   - Follow [development/SETUP_GUIDE.md](development/SETUP_GUIDE.md)

3. **Start implementing**:
   - Follow [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) Phase 1-9

### For DevOps

1. **Review architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Check deployment**: [deployment/DEPLOYMENT_GUIDE.md](deployment/DEPLOYMENT_GUIDE.md)
3. **Setup monitoring**: Prometheus + Grafana

### For Product/Business

1. **Review requirements**: [REQUIREMENT.md](REQUIREMENT.md)
2. **Check API capabilities**: [API.md](API.md)
3. **Try GraphQL Playground**: http://localhost:8000/graphql

---

## 💡 Tips for Navigation

### Finding Information

1. **Start with [docs/README.md](README.md)** - Central hub
2. **Use the search** - All docs are searchable
3. **Check the index** - Each doc has a table of contents
4. **Follow links** - Docs cross-reference each other

### Quick Lookup

- **How do I...?** → [docs/README.md](README.md#common-tasks--quick-links)
- **What is...?** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **Where is...?** → This file (PROJECT_OVERVIEW.md)
- **Why...?** → [ARCHITECTURE.md](ARCHITECTURE.md) explains decisions

---

## 📞 Getting Help

### Documentation Help
- [docs/README.md](README.md) - Documentation index
- Navigate by role, feature, or technology

### Technical Help
1. Check [ARCHITECTURE.md](ARCHITECTURE.md) for design questions
2. Check [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for how-to
3. Check [API.md](API.md) for API questions
4. Check [development/SETUP_GUIDE.md](development/SETUP_GUIDE.md) for setup issues

### Quick Links
- 📖 [Main README](../README.md)
- 📚 [Documentation Index](README.md)
- 🔌 [GraphQL API](API.md)
- 🏗️ [Architecture](ARCHITECTURE.md)

---

## 🎓 Recommended Reading Order

### First Day (2-3 hours)
1. This file (PROJECT_OVERVIEW.md) - 10 min
2. [REQUIREMENT.md](REQUIREMENT.md) - 15 min
3. [ARCHITECTURE.md](ARCHITECTURE.md) - 45 min
4. [Main README](../README.md) - 10 min
5. [API.md](API.md) - 30 min

### First Week
1. [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Study phases
2. [development/SETUP_GUIDE.md](development/SETUP_GUIDE.md) - Setup environment
3. Start implementing Phase 1-3

### Ongoing
- Reference [API.md](API.md) while building
- Follow [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) phases
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions

---

**Version:** 1.0.0
**Last Updated:** 2025-10-20
**Status:** Documentation Complete, Implementation Starting

# ShopX Sales Analytics - Quick Start Guide

Get your sales analytics dashboard running in **5 minutes** with **hot-reload** development!

## 🎯 Recommended: Docker Development (Hot-Reload)

**Fastest way to get started with automatic code reloading!**

### Prerequisites

- Docker Desktop installed and running
- Git installed
- That's it! No need to install Python, PostgreSQL, Redis, or Node.js

### Quick Start (5 minutes)

```bash
# 1. Navigate to project
cd claude-code-fastapi-graphql

# 2. Copy environment file
cp .env.example .env

# 3. Start everything with HOT-RELOAD
make dev-up

# 4. Run migrations (first time only)
make migrate-all

# 5. (Optional) Add sample data
make db-seed
```

**Done!** Your application is now running with hot-reload:
- Backend API: http://localhost:8000
- GraphQL Playground: http://localhost:8000/graphql
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Hot-Reload Magic ✨

Code changes auto-reload - no need to rebuild Docker images!

```bash
# Watch logs to see auto-reload
make dev-logs

# Edit any file in src/ and save
# You'll see: "WatchFiles detected changes in 'src/file.py'. Reloading..."
```

See [docs/HOT_RELOAD.md](docs/HOT_RELOAD.md) for details.

---

## 🐍 Alternative: Local Development (Without Docker)

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js 18+
- npm or yarn

### 1. Start Backend Services

```bash
# Start PostgreSQL (if not running)
brew services start postgresql@15

# Start Redis (if not running)
brew services start redis
```

### 2. Setup Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create database
createdb shopx_analytics

# Run migrations
alembic upgrade head

# Load sample data (optional)
python scripts/seed_data.py

# Start FastAPI server
uvicorn src.main:app --reload
```

Backend will be available at:
- API: http://localhost:8000
- GraphQL Playground: http://localhost:8000/graphql
- API Docs: http://localhost:8000/docs

### 3. Setup Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

Frontend will be available at:
- Dashboard: http://localhost:5173

### 4. Start Celery (Optional - for background tasks)

```bash
# Start Celery worker
celery -A src.celery_app worker --loglevel=info

# Start Celery beat scheduler
celery -A src.celery_app beat --loglevel=info
```

## Verify Installation

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Test GraphQL
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```

### Test Frontend

1. Open http://localhost:5173
2. You should see the Dashboard with:
   - Revenue metrics
   - Revenue trend chart
   - Top products table

### Test Redis Cache

```bash
# Check Redis connection
redis-cli ping
# Should return: PONG

# Check cache keys
redis-cli keys "analytics:*"
```

## What You Get

### Backend (FastAPI + GraphQL)
- ✅ 14 GraphQL queries
- ✅ 11 GraphQL mutations
- ✅ 8 database models
- ✅ Redis L1 cache (80%+ hit rate)
- ✅ Materialized views for analytics
- ✅ Partitioned tables for orders
- ✅ 70+ service methods
- ✅ 24 Celery background tasks

### Frontend (React + TypeScript)
- ✅ Dashboard with revenue charts
- ✅ Product management
- ✅ Customer analytics
- ✅ Sales rep leaderboard
- ✅ Apollo Client integration
- ✅ Tailwind CSS styling
- ✅ Recharts visualizations
- ✅ Responsive design

## Default URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | - |
| Backend API | http://localhost:8000 | - |
| GraphQL | http://localhost:8000/graphql | - |
| API Docs | http://localhost:8000/docs | - |
| Redoc | http://localhost:8000/redoc | - |
| PostgreSQL | localhost:5432 | See .env |
| Redis | localhost:6379 | - |

## Sample Data

Run the seed script to populate with sample data:

```bash
python scripts/seed_data.py
```

This creates:
- 50 products across 5 categories
- 100 customers
- 10 sales representatives
- 500 orders
- Analytics data

## Common Issues

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check PostgreSQL
psql -U postgres -c "SELECT version();"

# Recreate database
dropdb shopx_analytics
createdb shopx_analytics
alembic upgrade head
```

### Frontend won't start

```bash
# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

### GraphQL connection error

1. Ensure backend is running: http://localhost:8000/graphql
2. Check `.env` in frontend:
   ```
   VITE_GRAPHQL_URL=http://localhost:8000/graphql
   ```
3. Restart frontend: `npm run dev`

### Redis connection error

```bash
# Check Redis status
redis-cli ping

# Start Redis
brew services start redis
# Or
docker run -d -p 6379:6379 redis:7-alpine
```

## Development Workflow

### Making Backend Changes

```bash
# Watch for changes (auto-reload)
uvicorn src.main:app --reload

# Run tests
pytest

# Check types
mypy src/

# Format code
black src/
isort src/
```

### Making Frontend Changes

```bash
# Development server (hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## Next Steps

1. **Explore the Dashboard**
   - View revenue metrics
   - Analyze product performance
   - Check customer segments
   - Review sales rep leaderboard

2. **Test GraphQL API**
   - Open http://localhost:8000/graphql
   - Try sample queries
   - Test mutations

3. **Review Documentation**
   - [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)
   - [docs/API.md](docs/API.md)
   - [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
   - [frontend/FRONTEND_README.md](frontend/FRONTEND_README.md)

4. **Customize**
   - Add your own products
   - Modify analytics queries
   - Customize the UI theme
   - Add new features

## Production Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Docker deployment
- Cloud deployment (AWS, GCP, Azure)
- Environment configuration
- Performance tuning
- Monitoring setup

## Support

- GitHub Issues: [Report bugs](https://github.com/your-repo/issues)
- Documentation: [docs/](docs/)
- API Reference: http://localhost:8000/docs

---

**Built with**: FastAPI • GraphQL • React • TypeScript • Tailwind CSS • PostgreSQL • Redis • Celery

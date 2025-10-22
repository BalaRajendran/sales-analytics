# Start Development Environment

Start all necessary services for local development of the FastAPI GraphQL application.

## Instructions

1. Check if Docker is running (for PostgreSQL and Redis)
2. Start required services in the correct order
3. Verify each service is healthy
4. Start the FastAPI development server
5. Display access URLs and status

## Startup Sequence

### 1. Start Docker Services
```bash
docker-compose up -d postgres redis
```

Wait for services to be healthy:
```bash
docker-compose ps
```

### 2. Run Database Migrations (if needed)
```bash
alembic upgrade head
```

### 3. Start FastAPI Server
```bash
# Option 1: Using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Makefile
make dev

# Option 3: Using Docker Compose
docker-compose up api
```

### 4. Optional: Start Celery Worker
```bash
celery -A src.celery_app worker --loglevel=info
```

### 5. Optional: Start Celery Beat
```bash
celery -A src.celery_app beat --loglevel=info
```

## Verification Steps

1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps postgres
   ```

2. Check if Redis is running:
   ```bash
   docker-compose ps redis
   redis-cli ping
   ```

3. Check if API is responding:
   ```bash
   curl http://localhost:8000/health
   ```

4. Check GraphQL playground:
   Open http://localhost:8000/graphql in browser

## Display URLs

After startup, display:
- Backend API: http://localhost:8000
- GraphQL Playground: http://localhost:8000/graphql
- API Docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Common Issues

- Port already in use: Show which process is using the port
- Docker not running: Suggest starting Docker Desktop
- Database connection failed: Check .env configuration
- Redis connection failed: Verify Redis container health

## Cleanup

To stop all services:
```bash
docker-compose down
```

To stop and remove volumes:
```bash
docker-compose down -v
```

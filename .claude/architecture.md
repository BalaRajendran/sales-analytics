# URL Shortener - Architecture Documentation

## Deployment Architecture Decision

**Date:** 2025-01-12
**Decision:** Separate Docker containers for Frontend and Backend

### Architecture Overview

The application uses a **4-container architecture** for production deployment:

1. **Nginx** - Reverse proxy and SSL termination
2. **Frontend (React)** - Separate container running `serve` on port 3000
3. **Backend (FastAPI)** - Python API on port 8000
4. **PostgreSQL** - Database on port 5432
5. **Redis** - Cache/rate limiting on port 6379

### Container Communication Flow

```
Internet → Nginx (80/443) → {
    /api/* → FastAPI:8000
    /* → Frontend:3000
}
```

### Key Files

#### Frontend Production
- **Dockerfile:** `frontend/Dockerfile.prod` (multi-stage build with Bun and serve)
- **Dev Dockerfile:** `frontend/Dockerfile` (Vite dev server with Bun)
- **Service Name:** `frontend` (production), `frontend-dev` (development)
- **Port:** 3000 (internal only, not exposed)
- **Technology:** React 19 + Vite, built with Bun, served by `serve` package

#### Backend Production
- **Dockerfile:** `Dockerfile` (multi-stage build with uv)
- **Service Name:** `fastapi`
- **Port:** 8000 (internal only, not exposed)
- **Technology:** FastAPI + Gunicorn + Uvicorn workers
- **Important:** Does NOT serve static files (removed StaticFiles mounting)

#### Nginx
- **Image:** `nginx:alpine` (official image, no custom Dockerfile needed)
- **Config:** `nginx.conf` (mounted as volume)
- **SSL Certs:** `ssl/` directory (mounted as volume)
- **Service Name:** `nginx`
- **Ports:** 80, 443 (exposed to internet)
- **Purpose:** Routes traffic to frontend and backend containers

### Important: FastAPI Does NOT Serve Frontend

**Critical architectural point:** The FastAPI application (`src/main.py`) should **NOT** include any static file serving logic. The frontend is served by a separate Node.js container.

**Removed from src/main.py:**
```python
# ❌ INCORRECT - DO NOT ADD THIS
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(...))
```

**Correct approach:**
- FastAPI only handles API endpoints: `/api/*`, `/health`, `/docs`
- Frontend container serves React SPA
- Nginx proxies requests to appropriate container

### Docker Compose Services

**Production Deployment:**
```bash
make prod-up
```

**Active Services:**
- `postgres` - PostgreSQL database
- `redis` - Redis cache
- `fastapi` - Backend API
- `frontend` - React frontend (production build with Bun, served by `serve`)
- `nginx` - Reverse proxy

**Development Mode:**
```bash
make dev-up
```

**Active Services:**
- Same as production, PLUS:
- `frontend-dev` - React with hot reload (Vite dev server with Bun on port 5173)

### Why Separate Containers?

**User's requirement:** "I would create both as separate docker image and container"

**Benefits:**
1. **Independent Deployments** - Deploy frontend/backend separately
2. **Easier Rollbacks** - Roll back one without affecting the other
3. **Better Scaling** - Scale frontend and backend independently
4. **Development Flexibility** - Hot reload in dev, optimized in prod
5. **Clear Separation** - Frontend team can work independently

### Environment Variables

**Frontend Container:**
- `NODE_ENV=production`
- No direct API URL needed (proxied via Nginx)

**Backend Container:**
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `SECRET_KEY` - JWT/encryption key
- `CORS_ORIGINS` - Allowed origins
- `ENVIRONMENT=production`
- `DEBUG=false`

### Build Process

**Frontend Build:**
```dockerfile
# Stage 1: Build React app
FROM node:20-alpine AS builder
RUN npm ci && npm run build

# Stage 2: Serve with lightweight server
FROM node:20-alpine
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
CMD ["serve", "-s", "dist", "-l", "3000"]
```

**Backend Build:**
```dockerfile
# Stage 1: Build dependencies with uv
FROM python:3.12-slim AS backend-builder
RUN uv pip install --system -e .

# Stage 2: Runtime
FROM python:3.12-slim
COPY --from=backend-builder ...
CMD ["gunicorn", ...]
```

### Nginx Routing Rules

```nginx
upstream fastapi_backend {
    server fastapi:8000;
}

upstream frontend_app {
    server frontend:3000;
}

server {
    # API endpoints → FastAPI
    location /api/ {
        proxy_pass http://fastapi_backend;
    }

    # Health check → FastAPI
    location /health {
        proxy_pass http://fastapi_backend/health;
    }

    # Docs → FastAPI
    location ~ ^/(docs|redoc|openapi.json) {
        proxy_pass http://fastapi_backend;
    }

    # Everything else → Frontend
    location / {
        proxy_pass http://frontend_app;
    }
}
```

### Resource Allocation (Production)

**Frontend:**
- CPU: 0.25-0.5 cores
- Memory: 256-512 MB
- Restart: always

**Backend:**
- CPU: 1-2 cores
- Memory: 1-2 GB
- Workers: (CPU_COUNT * 2) + 1
- Restart: always

**Nginx:**
- CPU: 0.5-1 core
- Memory: 256-512 MB
- Restart: always

**PostgreSQL:**
- CPU: 0.5-1 core
- Memory: 512 MB - 1 GB
- Volume: postgres-data (persistent)

**Redis:**
- CPU: 0.25-0.5 cores
- Memory: 256-512 MB
- Volume: redis-data (persistent)

### Frontend Technologies

**Framework:** React 19
**Build Tool:** Vite 6
**Language:** TypeScript
**Production Server:** serve (NPM package)
**Dev Server:** Vite dev server
**Port:** 3000 (production), 5173 (development)

### Backend Technologies

**Framework:** FastAPI
**Server:** Gunicorn + Uvicorn workers
**Language:** Python 3.12
**Package Manager:** uv (ultra-fast)
**Database:** PostgreSQL 16
**Cache:** Redis 7
**Port:** 8000

### Security Considerations

1. **No Direct Port Exposure** - Only Nginx exposes ports externally
2. **Non-root Users** - All containers run as non-root
3. **Internal Network** - Services communicate via Docker network
4. **SSL/TLS** - Nginx handles SSL termination
5. **Rate Limiting** - Configured in both FastAPI and Nginx
6. **CORS** - Properly configured in FastAPI

### Deployment Checklist

- [ ] Build all containers: `docker compose build`
- [ ] Set environment variables in `.env`
- [ ] Configure SSL certificates in `ssl/` directory
- [ ] Start services: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`
- [ ] Run migrations: `docker compose exec fastapi alembic upgrade head`
- [ ] Verify health: `curl http://localhost/health`
- [ ] Test frontend: Visit `http://localhost` or your domain
- [ ] Check logs: `docker compose logs -f`

### Common Mistakes to Avoid

1. ❌ **Do NOT** add StaticFiles to FastAPI (`src/main.py`)
2. ❌ **Do NOT** expose internal ports in production (only Nginx should expose 80/443)
3. ❌ **Do NOT** build frontend inside FastAPI Dockerfile
4. ❌ **Do NOT** serve frontend directly from FastAPI
5. ✅ **DO** keep frontend and backend as separate containers
6. ✅ **DO** proxy all traffic through Nginx
7. ✅ **DO** use `frontend` service name for production builds

### Project Structure

```
url-shortner/
├── src/                          # FastAPI backend
│   ├── main.py                  # ⚠️ No StaticFiles mounting!
│   ├── api/
│   └── core/
├── frontend/                     # React frontend
│   ├── Dockerfile               # Dev build (Vite)
│   ├── Dockerfile.prod          # Production build (serve)
│   ├── src/
│   └── package.json
├── ssl/                         # SSL certificates (mounted to Nginx)
│   └── .gitkeep
├── docs/                        # All documentation
│   └── deployment/
│       └── EC2_DOCKER_DEPLOYMENT.md  # Complete deployment guide
├── nginx.conf                   # Nginx routing config (mounted to container)
├── Dockerfile                   # Backend production build
├── docker-compose.yml           # Base services
└── docker-compose.prod.yml      # Production overrides
```

**Note:** We use the official `nginx:alpine` image directly - no custom Nginx Dockerfile needed!

### Testing the Architecture

**Local Development:**
```bash
# Start all services with dev frontend
docker compose --profile dev up -d

# Frontend dev server: http://localhost:5173
# Backend API: http://localhost:8000
# Nginx proxy: http://localhost
```

**Production Simulation:**
```bash
# Start production services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# All traffic through Nginx: http://localhost
```

**Health Checks:**
```bash
# Check all services
docker compose ps

# Test API health
curl http://localhost/health

# Test frontend (should return HTML)
curl http://localhost/

# Check API endpoint
curl http://localhost/api/v1/...
```

### Scaling Strategies

**Horizontal Scaling:**
```bash
# Scale backend
docker compose up -d --scale fastapi=3

# Scale frontend
docker compose up -d --scale frontend=2
```

Nginx upstream blocks automatically load balance across multiple instances.

**Vertical Scaling:**
Edit `docker-compose.prod.yml` to increase CPU/memory limits.

### Monitoring

**Container Health:**
```bash
docker compose ps
docker stats
```

**Logs:**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f frontend
docker compose logs -f fastapi
docker compose logs -f nginx
```

**Metrics to Monitor:**
- Container CPU/Memory usage
- Response times (Nginx logs)
- Error rates (application logs)
- Database connections
- Redis hit rate

---

**Remember:** This architecture keeps frontend and backend as **independent, separately deployable containers** that communicate through Nginx as a reverse proxy. This provides maximum flexibility for deployments, rollbacks, and scaling.

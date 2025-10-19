# URL Shortener - EC2 Docker Deployment Guide

## Architecture Overview

This URL Shortener application uses a **4-container architecture** for production deployment:

```
┌─────────────────────────────────────────────────────────────┐
│                         Nginx (Port 80/443)                  │
│                   (Reverse Proxy + SSL Termination)          │
└──────────────┬─────────────────────────┬────────────────────┘
               │                         │
               │ /api/*                  │ /*
               │                         │
               ▼                         ▼
    ┌──────────────────┐      ┌──────────────────┐
    │   FastAPI        │      │   React Frontend │
    │   (Backend API)  │      │   (serve)        │
    │   Port 8000      │      │   Port 3000      │
    └────────┬─────────┘      └──────────────────┘
             │
             │ (Internal Network)
             │
    ┌────────┴─────────┬─────────────────┐
    │                  │                 │
    ▼                  ▼                 ▼
┌────────┐      ┌──────────┐      ┌─────────┐
│PostgreSQL│      │  Redis   │      │ Volumes │
│Port 5432│      │ Port 6379│      │ (Data)  │
└────────┘      └──────────┘      └─────────┘
```

### Container Roles

1. **Nginx (nginx:alpine)** - Official Nginx image, reverse proxy and SSL termination
2. **Frontend** - React application served by `serve` (Node.js)
3. **FastAPI** - Python backend API with Gunicorn + Uvicorn workers
4. **PostgreSQL** - Primary database
5. **Redis** - Rate limiting and caching

**Note:** We use the official `nginx:alpine` image directly with a mounted configuration file - no custom Dockerfile needed!

### Why Separate Frontend Container?

**Benefits of this architecture:**
- ✅ **Independent deployments** - Deploy frontend/backend separately
- ✅ **Easier rollbacks** - Roll back frontend or backend independently
- ✅ **Better scaling** - Scale frontend and backend containers independently
- ✅ **Development flexibility** - Hot reload in dev, optimized serve in prod
- ✅ **Clear separation of concerns** - Frontend team can work independently

## Prerequisites

- Ubuntu 22.04 LTS EC2 instance (t3.medium or larger recommended)
- Docker 24.0+
- Docker Compose V2
- Git
- Domain name pointed to EC2 instance (for SSL)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd url-shortner
```

### 2. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your production values
nano .env
```

**Required environment variables:**
```env
# Database
POSTGRES_USER=urlshortener
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=urlshortener
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=<generate-with: openssl rand -hex 32>

# Application
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Build and Start Services

```bash
# Build and start all services
make prod-up

# Check status
docker compose ps

# View logs
make prod-logs
```

### 4. Run Database Migrations

```bash
# Run migrations inside container
docker compose exec fastapi make migrate
```

### 5. Verify Deployment

```bash
# Check health endpoint
curl http://localhost/health

# Expected response:
# {"success": true, "data": {"status": "ok", "version": "1.0.0", ...}}
```

## Container Details

### Frontend Container (React + serve)

**Dockerfile:** `frontend/Dockerfile.prod`

- **Build Stage:** Builds React app with Vite using Bun
- **Runtime:** Lightweight Bun Alpine with `serve` package
- **Port:** 3000 (internal only)
- **User:** Non-root user `frontend` for security
- **Health Check:** HTTP check on port 3000

**Key Features:**
- Multi-stage build for minimal image size
- SPA routing enabled with `serve -s`
- Ultra-fast dependency installation with Bun
- Built assets cached in Docker layers

### Backend Container (FastAPI + Gunicorn)

**Dockerfile:** `Dockerfile`

- **Build Stage:** Uses `uv` for ultra-fast Python package installation
- **Runtime:** Python 3.12 slim with Gunicorn + Uvicorn workers
- **Port:** 8000 (internal only)
- **User:** Non-root user `appuser` for security
- **Workers:** `(CPU_COUNT * 2) + 1`

**Key Features:**
- Multi-stage build with `uv` package manager
- Gunicorn with Uvicorn workers for ASGI
- Graceful shutdown handling
- Comprehensive logging

### Nginx Container

**Image:** `nginx:alpine` (official Nginx image)

- **Configuration:** `nginx.conf` mounted as volume
- **Ports:** 80 (HTTP), 443 (HTTPS)
- **Health Check:** Checks `/health` endpoint
- **No custom Dockerfile needed!**

**Routing Rules:**
```nginx
/health       → FastAPI (passthrough)
/api/*        → FastAPI backend
/docs         → FastAPI (OpenAPI docs)
/redoc        → FastAPI (ReDoc)
/*            → React frontend
```

### PostgreSQL Container

- **Image:** postgres:16-alpine
- **Port:** 5432 (internal only in production)
- **Volume:** postgres-data (persistent)
- **Configuration:** Optimized for production

### Redis Container

- **Image:** redis:7-alpine
- **Port:** 6379 (internal only in production)
- **Volume:** redis-data (persistent)
- **Configuration:** AOF persistence enabled

## Docker Compose Files

### docker-compose.yml (Base Configuration)

Defines all services with development-friendly defaults:
- Exposed ports for direct access
- Volume mounts for development
- Health checks
- Network configuration

### docker-compose.prod.yml (Production Overrides)

Production-specific configurations:
- Resource limits (CPU, memory)
- Removed port exposures (security)
- Always restart policy
- JSON logging with rotation
- Performance tuning

**Usage:**
```bash
# Production deployment
make prod-up

# Development mode with frontend hot reload
make dev-up
```

## SSL/TLS Setup

### Option 1: Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install -y certbot

# Stop Nginx temporarily
docker compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to ssl directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/

# Update permissions
sudo chown -R $USER:$USER ssl/

# Restart Nginx
docker compose start nginx
```

### Option 2: Self-Signed Certificate (Testing)

```bash
# Generate self-signed certificate
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/privkey.pem \
  -out ssl/fullchain.pem
```

### Auto-Renewal Setup

```bash
# Create renewal hook
sudo nano /etc/letsencrypt/renewal-hooks/deploy/copy-certs.sh
```

```bash
#!/bin/bash
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /path/to/url-shortner/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /path/to/url-shortner/ssl/
docker compose restart nginx
```

```bash
# Make executable
sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/copy-certs.sh

# Test auto-renewal
sudo certbot renew --dry-run
```

## Deployment Commands

### Build Specific Service

**Advanced docker compose commands:**
```bash
# Build only frontend
docker compose build frontend

# Build only backend
docker compose build fastapi

# Build only nginx
docker compose build nginx
```

### Deploy Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and deploy everything
make prod-down
make prod-up

# Or rebuild specific service (advanced)
docker compose -f docker-compose.yml -f docker-compose.prod.yml build frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps frontend
```

### Rolling Updates (Zero Downtime)

**Advanced deployment strategy:**
```bash
# Update backend with scaling (requires manual docker compose)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale fastapi=2 --no-recreate
docker compose -f docker-compose.yml -f docker-compose.prod.yml stop fastapi
docker compose -f docker-compose.yml -f docker-compose.prod.yml rm -f fastapi
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d fastapi
```

## Monitoring and Logs

### View Logs

```bash
# All services
make prod-logs

# Specific service
docker compose logs -f fastapi
docker compose logs -f frontend
docker compose logs -f nginx

# Advanced options
docker compose logs --tail=100 fastapi  # Last 100 lines
docker compose logs --since 1h  # Logs since 1 hour ago
```

### Container Stats

```bash
# Real-time resource usage
docker stats

# Specific container
docker stats urlshortener-fastapi
```

### Health Checks

```bash
# Check all container health
docker compose ps

# Manual health check
curl http://localhost/health
```

## Backup and Restore

### Database Backup

```bash
# Create backup directory
mkdir -p backups

# Backup database
docker compose exec postgres pg_dump -U urlshortener urlshortener > backups/db_$(date +%Y%m%d_%H%M%S).sql

# Backup with compression
docker compose exec postgres pg_dump -U urlshortener urlshortener | gzip > backups/db_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Database Restore

```bash
# Restore from backup
cat backups/db_20240101_120000.sql | docker compose exec -T postgres psql -U urlshortener urlshortener

# Restore from compressed backup
gunzip < backups/db_20240101_120000.sql.gz | docker compose exec -T postgres psql -U urlshortener urlshortener
```

### Volume Backup

```bash
# Backup all volumes
docker run --rm \
  -v urlshortener_postgres-data:/source \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres-volume-$(date +%Y%m%d).tar.gz -C /source .
```

## Scaling

### Horizontal Scaling

**Advanced scaling (requires manual docker compose):**
```bash
# Scale FastAPI backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale fastapi=3

# Scale frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale frontend=2
```

**Note:** Nginx is configured with `upstream` blocks that automatically load balance across multiple container instances.

### Vertical Scaling

Edit `docker-compose.prod.yml` to adjust resource limits:

```yaml
fastapi:
  deploy:
    resources:
      limits:
        cpus: '4.0'      # Increase CPU
        memory: 4G       # Increase memory
      reservations:
        cpus: '2.0'
        memory: 2G
```

Then restart:
```bash
make prod-down
make prod-up
```

## Troubleshooting

### Container Won't Start

```bash
# Check container status
docker compose ps

# View detailed logs
docker compose logs <service-name>

# Inspect container
docker inspect <container-name>
```

### Frontend Not Loading

```bash
# Check frontend container logs
docker compose logs frontend

# Verify frontend is running
docker compose exec frontend wget -O- http://localhost:3000

# Check Nginx configuration
docker compose exec nginx nginx -t

# Reload Nginx
docker compose exec nginx nginx -s reload
```

### Database Connection Issues

```bash
# Check database is running
docker compose exec postgres pg_isready

# Test connection from FastAPI
docker compose exec fastapi python -c "from src.core.database import engine; print(engine.connect())"

# Check DATABASE_URL
docker compose exec fastapi env | grep DATABASE_URL
```

### Port Already in Use

```bash
# Find process using port 80
sudo lsof -i :80

# Stop conflicting service
sudo systemctl stop apache2  # or nginx, etc.

# Or change port in .env
NGINX_HTTP_PORT=8080
```

## Performance Tuning

### Gunicorn Workers

Edit `gunicorn.conf.py`:

```python
workers = (multiprocessing.cpu_count() * 2) + 1  # Adjust multiplier
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000  # Increase for more concurrent requests
```

### PostgreSQL Tuning

Edit `docker-compose.yml` or create `deployment/postgres/postgresql.conf`:

```conf
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
work_mem = 5MB
```

### Redis Tuning

```bash
# Set maxmemory and eviction policy
docker compose exec redis redis-cli CONFIG SET maxmemory 512mb
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` file to version control
2. **Secrets Management**: Consider using Docker secrets or AWS Secrets Manager
3. **Network Isolation**: Only Nginx exposes ports externally
4. **Non-root Users**: All containers run as non-root users
5. **Regular Updates**: Keep base images and dependencies updated
6. **SSL/TLS**: Always use HTTPS in production
7. **Rate Limiting**: Configured in both FastAPI and Nginx
8. **CORS**: Properly configured in FastAPI settings

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to EC2

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to EC2
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /path/to/url-shortner
            git pull origin main
            docker compose -f docker-compose.yml -f docker-compose.prod.yml build
            docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
            docker compose exec fastapi alembic upgrade head
```

## Development vs Production

### Development Mode

```bash
# Start with dev profile (includes frontend-dev with hot reload)
make dev-up

# Frontend available at: http://localhost:5173
# Backend API at: http://localhost:8000
```

### Production Mode

```bash
# Production deployment
make prod-up

# All traffic goes through Nginx: http://localhost (or your domain)
```

## Resource Requirements

### Minimum Requirements

- **CPU:** 2 vCPUs
- **RAM:** 4 GB
- **Storage:** 20 GB
- **EC2 Instance:** t3.medium

### Recommended for Production

- **CPU:** 4 vCPUs
- **RAM:** 8 GB
- **Storage:** 50 GB (with backups)
- **EC2 Instance:** t3.large or c5.xlarge

## Support and Maintenance

### Health Monitoring

Set up external monitoring for:
- `https://yourdomain.com/health` - Application health
- Container status via Docker socket or API
- Disk space and system resources

### Log Rotation

Logs are automatically rotated with Docker's JSON file driver:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "50m"
    max-file: "5"
```

### Regular Maintenance Tasks

- Weekly: Review logs for errors
- Weekly: Check disk space usage
- Monthly: Update dependencies and rebuild
- Monthly: Review and rotate database backups
- Quarterly: Security audit and penetration testing

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Configuration Guide](https://nginx.org/en/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)

## Getting Help

If you encounter issues:

1. Check container logs: `docker compose logs -f`
2. Verify environment variables: `docker compose config`
3. Test each service individually
4. Review this documentation
5. Open an issue in the repository

---

**Last Updated:** 2025-01-12
**Version:** 1.0.0

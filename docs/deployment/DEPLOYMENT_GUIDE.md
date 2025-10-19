# Deployment Guide

Quick guide for deploying the URL Shortener to various platforms.

> **📦 For comprehensive Docker deployment to EC2:** See [EC2 Docker Deployment Guide](EC2_DOCKER_DEPLOYMENT.md) for complete production setup with Nginx, separate frontend/backend containers, PostgreSQL, Redis, SSL, monitoring, and scaling.

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] SECRET_KEY is strong and unique
- [ ] DEBUG=false in production
- [ ] CORS origins properly configured
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] SSL certificates ready
- [ ] Domain name configured

## Environment Configuration

### Production Environment Variables

Create a `.env.production` file:

```env
# Application
PROJECT_NAME="URL Shortener API"
VERSION="0.1.0"
DEBUG=false
ENVIRONMENT=production

# Server
HOST=0.0.0.0
PORT=8000

# API
API_V1_PREFIX=/api/v1

# CORS - Update with your frontend domain
CORS_ORIGINS=["https://yourdomain.com"]

# Database - Use PostgreSQL in production
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/url_shortener

# Security - MUST change in production!
SECRET_KEY=<generate-strong-random-key-here>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# URL Shortener Settings
SHORT_URL_LENGTH=6
BASE_URL=https://yourdomain.com
```

### Generate Strong Secret Key

```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

## Database Setup

### PostgreSQL

#### 1. Install PostgreSQL

```bash
# Ubuntu
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql@16
```

#### 2. Create Database

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE url_shortener;
CREATE USER url_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE url_shortener TO url_user;
\q
```

#### 3. Configure Connection

Update DATABASE_URL in `.env.production`:
```env
DATABASE_URL=postgresql+asyncpg://url_user:strong_password@localhost:5432/url_shortener
```

#### 4. Run Migrations

```bash
cd backend
make migrate
```

## Deployment Options

### Option 1: Docker Deployment (Recommended)

> **📦 For complete Docker production setup:** See our comprehensive [EC2 Docker Deployment Guide](EC2_DOCKER_DEPLOYMENT.md)

The guide covers:
- **4-container architecture**: Nginx (reverse proxy), Frontend (React), Backend (FastAPI), PostgreSQL, Redis
- **Separate containers**: Independent frontend and backend deployments
- **Production optimizations**: Multi-stage builds with `uv`, Gunicorn workers, resource limits
- **SSL/TLS setup**: Let's Encrypt configuration and auto-renewal
- **Monitoring & Logging**: Health checks, log rotation, container stats
- **Scaling strategies**: Horizontal and vertical scaling
- **Backup & Restore**: Database and volume backups
- **Troubleshooting**: Common issues and solutions

**Quick Start:**
```bash
# Clone repository
git clone <your-repo>
cd url-shortner

# Configure environment
cp .env.example .env
# Edit .env with your production values

# Deploy with Docker Compose
make prod-up

# Run migrations (inside container)
docker compose exec fastapi make migrate

# Check status
docker compose ps
curl http://localhost/health
```

### Option 2: Traditional Server Deployment

#### 1. Set Up Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.12 python3.12-venv postgresql nginx -y
```

#### 2. Deploy Application

```bash
# Create app directory
sudo mkdir -p /opt/url-shortener
sudo chown $USER:$USER /opt/url-shortener

# Clone or copy code
cd /opt/url-shortener
git clone <your-repo> .

# Set up backend
cd backend
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

#### 3. Create Systemd Service

```ini
# /etc/systemd/system/url-shortener.service
[Unit]
Description=URL Shortener API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/url-shortener/backend
Environment="PATH=/opt/url-shortener/backend/.venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/opt/url-shortener/backend/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable url-shortener
sudo systemctl start url-shortener
sudo systemctl status url-shortener
```

#### 4. Configure Nginx

```nginx
# /etc/nginx/sites-available/url-shortener
server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        root /opt/url-shortener/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/url-shortener /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. Set Up SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
```

### Option 3: Cloud Platform Deployment

#### AWS (Elastic Beanstalk)

1. **Create application:**
   ```bash
   eb init -p python-3.12 url-shortener
   ```

2. **Create environment:**
   ```bash
   eb create production-env
   ```

3. **Configure environment variables:**
   ```bash
   eb setenv DATABASE_URL="..." SECRET_KEY="..." DEBUG=false
   ```

4. **Deploy:**
   ```bash
   eb deploy
   ```

#### Heroku

1. **Create app:**
   ```bash
   heroku create url-shortener-api
   ```

2. **Add PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set SECRET_KEY="..."
   heroku config:set DEBUG=false
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

5. **Run migrations:**
   ```bash
   heroku run make migrate
   ```

#### Railway

1. **Create new project** on railway.app

2. **Add PostgreSQL** database

3. **Deploy from GitHub** repository

4. **Set environment variables** in dashboard

5. **Migrations run automatically** on deploy

## Frontend Deployment

### Build Frontend

```bash
cd frontend
bun run build
```

### Deploy Options

#### Vercel
```bash
bun add -g vercel
vercel --prod
```

#### Netlify
```bash
bun add -g netlify-cli
netlify deploy --prod --dir=dist
```

#### Static Hosting (S3, Cloudflare Pages)
Upload `dist/` folder contents

### Configure Backend URL

Update frontend API client to point to production backend:

```typescript
// src/config.ts
export const API_BASE_URL = import.meta.env.PROD
  ? 'https://api.yourdomain.com'
  : 'http://localhost:8000';
```

## Database Migrations

### Running Migrations in Production

```bash
# Preview what will be migrated (advanced)
uv run alembic upgrade head --sql

# Run migration
make migrate

# Rollback if needed (advanced)
uv run alembic downgrade -1
```

### Zero-Downtime Migrations

1. **Add new column with default:**
   ```python
   # Migration
   op.add_column('urls', sa.Column('new_field', sa.String(), nullable=True))
   ```

2. **Deploy application code** (doesn't use new column yet)

3. **Backfill data** if needed:
   ```sql
   UPDATE urls SET new_field = 'default' WHERE new_field IS NULL;
   ```

4. **Deploy code** that uses new column

5. **Make column non-nullable** if needed (separate migration)

## Monitoring & Logging

### Application Logging

Configure structured logging:

```python
# src/core/logging.py
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
```

### Health Checks

```bash
# Check API health
curl https://yourdomain.com/health

# Check database connection
curl https://yourdomain.com/health/db
```

### Monitoring Tools

- **Sentry**: Error tracking
- **DataDog**: APM and metrics
- **Prometheus + Grafana**: Metrics and dashboards
- **CloudWatch**: AWS monitoring

## Backup Strategy

### Database Backups

#### Automated PostgreSQL Backups

```bash
# Create backup script
cat > /opt/backups/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U url_user url_shortener | gzip > \
  $BACKUP_DIR/url_shortener_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
EOF

chmod +x /opt/backups/backup-db.sh
```

#### Schedule with Cron

```bash
# Add to crontab
0 2 * * * /opt/backups/backup-db.sh
```

### Application Backups

- Code: Version controlled in Git
- Environment: Documented in .env.example
- Static files: If any, backup to S3/Cloudflare R2

## Security Hardening

### 1. Update Dependencies Regularly

```bash
cd backend
uv sync --upgrade
```

### 2. Enable HTTPS Only

```python
# Redirect HTTP to HTTPS
if not request.url.scheme == "https":
    return RedirectResponse(url=str(request.url.replace(scheme="https")))
```

### 3. Set Security Headers

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
)
```

### 4. Rate Limiting (Future)

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/urls/")
@limiter.limit("10/minute")
async def create_url(...):
    pass
```

### 5. Database Connection Pooling

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Performance Optimization

### 1. Enable Gzip Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 2. Add Caching Headers

```python
@app.get("/api/v1/urls/{short_code}/stats")
async def get_stats(...):
    return Response(
        content=...,
        headers={"Cache-Control": "public, max-age=60"}
    )
```

### 3. Database Indexes

Ensure indexes exist (already in migrations):
```sql
CREATE INDEX idx_short_code ON urls(short_code);
CREATE INDEX idx_original_url ON urls(original_url);
```

### 4. Connection Pooling

Configure appropriate pool size based on load.

## Scaling

### Horizontal Scaling

```
Load Balancer (nginx/HAProxy)
    ├─> App Server 1
    ├─> App Server 2
    └─> App Server 3
         │
         ▼
    PostgreSQL
```

### Running Multiple Workers

```bash
# With Gunicorn
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Database Read Replicas

Configure read replicas for heavy read workloads.

## Troubleshooting

### Application Won't Start

1. Check logs: `journalctl -u url-shortener -f`
2. Verify environment variables
3. Test database connection
4. Check file permissions

### High Memory Usage

1. Reduce worker count
2. Check for memory leaks
3. Monitor with `htop` or similar

### Slow Responses

1. Check database query performance
2. Add indexes if needed
3. Enable query logging
4. Consider caching

## Rollback Plan

### Quick Rollback

```bash
# Docker (production)
make prod-down
git checkout previous-version
make prod-up

# Traditional deployment
cd /opt/url-shortener
git checkout previous-version
sudo systemctl restart url-shortener
```

### Database Rollback

**Advanced alembic commands:**
```bash
# Rollback one migration
uv run alembic downgrade -1

# Rollback to specific version
uv run alembic downgrade <revision>
```

## Post-Deployment

- [ ] Verify health endpoint
- [ ] Test URL creation
- [ ] Test redirects
- [ ] Check logs for errors
- [ ] Monitor metrics
- [ ] Verify backups running
- [ ] Test failover (if applicable)
- [ ] Update documentation

## Support

For deployment issues:
1. Check logs first
2. Review this guide
3. Consult FastAPI documentation
4. Open GitHub issue if needed

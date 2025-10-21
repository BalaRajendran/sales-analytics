# Hot-Reload Development Setup

This document explains how the hot-reload functionality works for the FastAPI backend.

## Overview

The development environment uses **Uvicorn's built-in file watcher** to automatically reload the FastAPI application when source code changes are detected, eliminating the need to manually rebuild Docker images during development.

**TL;DR:** Use `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d` for hot-reload.

## How It Works

### 1. Volume Mounts

The `docker-compose.yml` file mounts your local source code into the container:

```yaml
volumes:
  - ./src:/app/src  # Mount source code for hot-reload
  - ./migrations:/app/migrations  # Mount migrations
  - ./gunicorn.dev.conf.py:/app/gunicorn.dev.conf.py  # Mount dev config
  - ./logs:/app/logs  # Application logs
```

This means changes to files in `./src` or `./migrations` are immediately reflected inside the container.

### 2. Development Docker Compose Override

The `docker-compose.dev.yml` file overrides the default configuration to use Uvicorn with hot-reload:

```yaml
command: >
  uvicorn src.main:app
  --host 0.0.0.0
  --port 8000
  --reload                      # Enable auto-reload
  --reload-dir /app/src         # Watch src directory
  --reload-dir /app/migrations  # Watch migrations directory
  --log-level debug             # Verbose logging
```

**Why Uvicorn instead of Gunicorn?**
- Uvicorn's `--reload` flag uses WatchFiles for reliable file detection
- Faster and more stable reload mechanism than Gunicorn's reload
- Better for development; Gunicorn is still used in production

### 3. Two-File Compose Setup

Development uses docker-compose's override feature:

```bash
# Development (with hot-reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production (no hot-reload, multi-worker Gunicorn)
docker-compose up -d
```

## Usage

### Starting the Development Environment

```bash
# Start with hot-reload using the dev override
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Or just start the FastAPI service
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d fastapi
```

### Verifying Hot-Reload is Enabled

Check the logs to confirm hot-reload is active:

```bash
docker logs shopx-analytics-api | grep "reloader"
```

You should see:
```
INFO:     Started reloader process [1] using WatchFiles
INFO:     Will watch for changes in these directories: ['/app/migrations', '/app/src']
```

### Making Code Changes

1. Edit any file in `./src/` directory
2. Save the file
3. Watch the logs to see the reload:

```bash
docker logs -f shopx-analytics-api
```

You'll see:
```
WARNING:  WatchFiles detected changes in 'src/your_file.py'. Reloading...
INFO:     Shutting down
INFO:     Application shutdown complete.
INFO:     Finished server process [8]
INFO:     Started server process [20]
INFO:     Application startup complete.
```

### Testing a Change

Try making a small change to test:

```python
# Edit src/main.py
print("Starting Sales Dashboard API... [DEVELOPMENT]")
```

Watch the logs:
```bash
docker logs -f shopx-analytics-api
```

## Troubleshooting

### Changes Not Detected

If changes aren't being detected:

1. **Check volume mounts:**
   ```bash
   docker inspect shopx-analytics-api | grep -A 10 Mounts
   ```

2. **Verify config:**
   ```bash
   docker exec shopx-analytics-api env | grep GUNICORN_CONFIG
   ```

3. **Restart the container:**
   ```bash
   docker-compose restart fastapi
   ```

### Worker Not Restarting

If the worker detects changes but doesn't restart properly:

1. Check for Python syntax errors in your code
2. Look for import errors in the logs
3. Try a full restart:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Performance Issues

Hot-reload uses file watching which can be resource-intensive:

- On macOS, Docker Desktop's file sharing can be slow
- Consider using Docker's `delegated` mount mode for better performance:
  ```yaml
  volumes:
    - ./src:/app/src:delegated
  ```

## Production Deployment

**Important:** Never use hot-reload in production!

For production, set:
```bash
GUNICORN_CONFIG=gunicorn.conf.py
```

This uses:
- Multiple workers (CPU cores × 2 + 1)
- Application preloading
- No file watching
- Optimized for performance

## Files Watched

The following directories/files trigger reloads when modified:

- `./src/**/*.py` - All Python source files
- `./migrations/**/*.py` - Migration scripts
- Any file imported by your application

Note: Changes to `gunicorn.dev.conf.py` require a container restart.

## Performance Comparison

| Aspect | Hot-Reload (Dev) | Full Rebuild |
|--------|------------------|--------------|
| Change Detection | < 1 second | N/A |
| Reload Time | 2-5 seconds | 30-60 seconds |
| Resource Usage | Low | High (CPU/disk) |
| Docker Build | Not needed | Required |

## Best Practices

1. **Use for Development Only**: Hot-reload is for local development
2. **Commit .env with Production Config**: Keep production settings in version control
3. **Watch Logs**: Monitor reload behavior to catch errors early
4. **Test Changes**: Verify functionality after each reload
5. **Restart Periodically**: Full restart occasionally to clear any state

## Quick Reference

```bash
# Development with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production without hot-reload
docker-compose up -d

# Check if hot-reload is active
docker logs shopx-analytics-api | grep "reloader"

# Watch for reloads in real-time
docker logs -f shopx-analytics-api

# Restart after dependency changes
docker-compose build fastapi
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Related Files

- `docker-compose.yml` - Base Docker Compose configuration
- `docker-compose.dev.yml` - Development overrides with Uvicorn hot-reload
- `gunicorn.conf.py` - Production Gunicorn settings (multi-worker)
- `docs/DEVELOPMENT.md` - Quick development setup guide

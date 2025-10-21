# Development Setup

Quick guide for local development with hot-reload enabled.

## Quick Start

### 1. Start Development Environment

```bash
# Start all services with hot-reload enabled
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Or use the shorthand
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d fastapi
```

### 2. Verify Hot-Reload is Active

```bash
docker logs shopx-analytics-api | grep "reloader"
```

You should see:
```
INFO:     Started reloader process [1] using WatchFiles
INFO:     Will watch for changes in these directories: ['/app/migrations', '/app/src']
```

### 3. Make Changes and Watch Auto-Reload

Edit any Python file in `./src/` and save it:

```bash
# Watch the logs to see reloading in action
docker logs -f shopx-analytics-api
```

You'll see something like:
```
WARNING:  WatchFiles detected changes in 'src/your_file.py'. Reloading...
INFO:     Shutting down
INFO:     Application shutdown complete.
INFO:     Started server process [XX]
INFO:     Application startup complete.
```

## What's Configured

### Volume Mounts
The following directories are mounted for live code updates:
- `./src` → `/app/src` (source code)
- `./migrations` → `/app/migrations` (database migrations)
- `./logs` → `/app/logs` (application logs)

### Uvicorn Auto-Reload
The development configuration uses Uvicorn's built-in file watcher:
- Watches `src/` and `migrations/` directories
- Auto-reloads on Python file changes
- Typical reload time: 2-3 seconds

## Daily Workflow

```bash
# Morning: Start services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# During development: Make changes to files in ./src
# Changes are detected automatically - no rebuild needed!

# Optional: Watch logs while developing
docker logs -f shopx-analytics-api

# Evening: Stop services (optional)
docker-compose down
```

## Troubleshooting

### Hot-Reload Not Working?

1. **Check if dev override is active:**
   ```bash
   docker ps --format "table {{.Names}}\t{{.Command}}" | grep shopx
   ```
   Should show: `uvicorn src.main:app --host...`

2. **Restart with dev configuration:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

3. **Check file permissions:**
   ```bash
   ls -la src/
   # Ensure files are readable
   ```

### Changes Not Appearing?

1. **Verify volume mounts:**
   ```bash
   docker exec shopx-analytics-api ls -la /app/src
   ```

2. **Check for syntax errors:**
   ```bash
   docker logs shopx-analytics-api | grep -i error
   ```

3. **Manual reload:**
   ```bash
   docker-compose restart fastapi
   ```

## Production Deployment

**Important:** For production, use the standard compose file without the dev override:

```bash
# Production (no hot-reload)
docker-compose up -d
```

This uses Gunicorn with multiple workers for better performance.

## Files Structure

```
.
├── docker-compose.yml          # Base configuration
├── docker-compose.dev.yml      # Development overrides (hot-reload)
├── src/                        # Your code (auto-reloaded)
├── migrations/                 # Database migrations (auto-reloaded)
└── logs/                       # Application logs
```

## Common Commands

```bash
# Start with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker logs -f shopx-analytics-api

# Restart specific service
docker-compose restart fastapi

# Stop all services
docker-compose down

# Rebuild and restart (if dependencies changed)
docker-compose build fastapi
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

## Tips

- ✅ **No rebuild needed** for code changes in `./src`
- ✅ **Restart required** if you change `pyproject.toml` or add new dependencies
- ✅ **Watch logs** to see reload messages and catch errors early
- ✅ **Use production mode** for actual deployment

## Next Steps

- Check [docs/HOT_RELOAD.md](docs/HOT_RELOAD.md) for detailed technical information
- See [README.md](README.md) for general project documentation

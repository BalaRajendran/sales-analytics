# Celery Background Tasks Guide

Complete guide for running and managing background tasks in the Sales Dashboard API.

## Overview

The application uses Celery for background task processing with Redis as the broker and result backend.

**3 Task Queues:**
- `analytics` - Analytics calculations, MV refresh, cache warming
- `maintenance` - Database maintenance, cleanup, health checks
- `notifications` - Alerts, reports, monitoring

## Quick Start

### 1. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or using Homebrew (macOS)
brew services start redis
```

### 2. Start Celery Worker

```bash
# Start worker for all queues
celery -A src.celery_app worker --loglevel=info

# Start worker for specific queue
celery -A src.celery_app worker --loglevel=info -Q analytics

# Start multiple workers
celery -A src.celery_app worker --loglevel=info -Q analytics &
celery -A src.celery_app worker --loglevel=info -Q maintenance &
celery -A src.celery_app worker --loglevel=info -Q notifications &
```

### 3. Start Celery Beat (Scheduler)

```bash
# Start beat scheduler for periodic tasks
celery -A src.celery_app beat --loglevel=info
```

### 4. Start Flower (Monitoring UI)

```bash
# Install flower
pip install flower

# Start Flower
celery -A src.celery_app flower --port=5555

# Access at http://localhost:5555
```

## Scheduled Tasks

### Analytics Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `refresh_realtime_materialized_views` | Every 5 min | Refresh hourly metrics MV |
| `refresh_daily_materialized_views` | Every hour | Refresh daily aggregation MVs |
| `warm_dashboard_cache` | Every 2 min | Pre-populate dashboard cache |
| `generate_monthly_report` | 1st @ 6 AM | Generate monthly performance report |

### Maintenance Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `update_customer_segments` | Daily @ 2 AM | Update customer segments |
| `update_customer_lifetime_values` | Daily @ 3 AM | Recalculate customer LTV |
| `clean_old_order_partitions` | Sunday @ 4 AM | Drop partitions > 24 months old |

### Notification Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `check_low_stock_products` | Daily @ 9 AM | Alert for low stock |
| `send_daily_summary` | Daily @ 8 AM | Send yesterday's summary |
| `weekly_performance_report` | Monday @ 8 AM | Send weekly report |

## Manual Task Execution

### From Python Code

```python
from src.tasks.analytics_tasks import refresh_all_materialized_views
from src.tasks.maintenance_tasks import update_customer_segments

# Execute task asynchronously
result = refresh_all_materialized_views.delay()

# Wait for result
result.get(timeout=60)

# Execute with arguments
from src.tasks.analytics_tasks import export_analytics_data
result = export_analytics_data.delay(
    start_date="2024-01-01T00:00:00Z",
    end_date="2024-01-31T23:59:59Z",
    export_format="json"
)
```

### From Command Line

```bash
# Execute task
celery -A src.celery_app call src.tasks.analytics_tasks.refresh_all_materialized_views

# With arguments
celery -A src.celery_app call src.tasks.analytics_tasks.export_analytics_data \
  --args='["2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z"]' \
  --kwargs='{"export_format": "json"}'
```

### From GraphQL API

```graphql
mutation {
  triggerBackgroundTask(
    taskName: "refresh_all_materialized_views"
  ) {
    success
    taskId
    message
  }
}
```

## Task Monitoring

### Check Task Status

```python
from celery.result import AsyncResult
from src.celery_app import celery_app

# Get task result
result = AsyncResult(task_id, app=celery_app)

print(f"Status: {result.status}")
print(f"Result: {result.result}")
print(f"Traceback: {result.traceback}")
```

### View Active Tasks

```bash
# Inspect active tasks
celery -A src.celery_app inspect active

# Inspect scheduled tasks
celery -A src.celery_app inspect scheduled

# Inspect registered tasks
celery -A src.celery_app inspect registered
```

### View Task History

```bash
# View stats
celery -A src.celery_app inspect stats

# View queues
celery -A src.celery_app inspect active_queues
```

## Production Deployment

### Using Supervisor

Create `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery-worker-analytics]
command=/path/to/venv/bin/celery -A src.celery_app worker --loglevel=info -Q analytics --concurrency=4
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/worker-analytics.err.log
stdout_logfile=/var/log/celery/worker-analytics.out.log

[program:celery-worker-maintenance]
command=/path/to/venv/bin/celery -A src.celery_app worker --loglevel=info -Q maintenance --concurrency=2
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/worker-maintenance.err.log
stdout_logfile=/var/log/celery/worker-maintenance.out.log

[program:celery-beat]
command=/path/to/venv/bin/celery -A src.celery_app beat --loglevel=info
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/celery/beat.err.log
stdout_logfile=/var/log/celery/beat.out.log

[group:celery]
programs=celery-worker-analytics,celery-worker-maintenance,celery-beat
```

### Using Docker Compose

Add to `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery-worker:
    build: .
    command: celery -A src.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db

  celery-beat:
    build: .
    command: celery -A src.celery_app beat --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2

  flower:
    build: .
    command: celery -A src.celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
      - CELERY_RESULT_BACKEND=redis://redis:6379/2

volumes:
  redis_data:
```

### Using Systemd

Create `/etc/systemd/system/celery-worker.service`:

```ini
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A src.celery_app worker --loglevel=info --pidfile=/var/run/celery/worker.pid
PIDFile=/var/run/celery/worker.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

## Performance Tuning

### Worker Concurrency

```bash
# Auto-detect (CPU count)
celery -A src.celery_app worker

# Set specific concurrency
celery -A src.celery_app worker --concurrency=8

# Use gevent pool for I/O bound tasks
celery -A src.celery_app worker --pool=gevent --concurrency=100
```

### Task Priorities

Tasks are prioritized 0-9 (9 = highest):

```python
# High priority
refresh_realtime_mv.apply_async(priority=9)

# Normal priority
update_customer_segments.apply_async(priority=5)

# Low priority
clean_old_partitions.apply_async(priority=3)
```

### Memory Management

```bash
# Restart worker after 1000 tasks (prevent memory leaks)
celery -A src.celery_app worker --max-tasks-per-child=1000

# Set memory limit (restart if exceeded)
celery -A src.celery_app worker --max-memory-per-child=512000  # 512MB
```

## Troubleshooting

### Task Not Executing

```bash
# Check if worker is running
celery -A src.celery_app inspect active

# Check task registration
celery -A src.celery_app inspect registered

# Check queue
celery -A src.celery_app inspect active_queues

# Purge all tasks
celery -A src.celery_app purge
```

### High Task Latency

```bash
# Check number of workers
celery -A src.celery_app inspect stats

# Increase concurrency
celery -A src.celery_app worker --concurrency=16

# Add more workers
celery -A src.celery_app multi start worker1 worker2 worker3
```

### Failed Tasks

```python
# Retry failed task
from celery.result import AsyncResult
result = AsyncResult(task_id, app=celery_app)
result.retry()

# Get failure info
print(result.traceback)
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli ping

# Check Redis memory usage
redis-cli info memory

# Check Redis connected clients
redis-cli client list
```

## Best Practices

1. **Use Task Queues**: Separate tasks by priority and type
2. **Set Time Limits**: Prevent hung tasks with `task_time_limit`
3. **Enable Result Expiry**: Clear old results with `result_expires`
4. **Monitor with Flower**: Use Flower UI for real-time monitoring
5. **Use Retries**: Add retry logic for transient failures
6. **Log Everything**: Use structured logging for debugging
7. **Test Tasks**: Write tests for task logic
8. **Graceful Shutdown**: Use `worker_shutdown_timeout`

## Task Development

### Creating a New Task

```python
from src.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(
    name="src.tasks.my_tasks.my_new_task",
    bind=True,  # Access task instance as self
    max_retries=3,
    default_retry_delay=60,  # 1 minute
)
def my_new_task(self, arg1, arg2):
    """Task description."""
    try:
        # Task logic here
        result = do_something(arg1, arg2)

        logger.info(f"✓ Task completed: {result}")
        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(f"Task failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
```

### Adding to Beat Schedule

Edit `src/celery_app.py`:

```python
celery_app.conf.beat_schedule = {
    "my-new-task": {
        "task": "src.tasks.my_tasks.my_new_task",
        "schedule": crontab(hour=12, minute=0),  # Daily at noon
        "args": ("arg1_value", "arg2_value"),
        "options": {"priority": 5},
    },
}
```

## Monitoring Metrics

### Key Metrics to Monitor

- Task throughput (tasks/sec)
- Task latency (avg execution time)
- Failed task rate
- Queue depth
- Worker memory usage
- Redis memory usage
- Cache hit rate (for analytics tasks)

### Prometheus Integration

```python
from celery.signals import task_prerun, task_postrun, task_failure
from prometheus_client import Counter, Histogram

# Define metrics
task_counter = Counter('celery_task_total', 'Total tasks', ['task_name', 'status'])
task_duration = Histogram('celery_task_duration_seconds', 'Task duration', ['task_name'])

@task_prerun.connect
def task_start_handler(sender=None, task_id=None, task=None, **kwargs):
    task_counter.labels(task_name=task.name, status='started').inc()

@task_postrun.connect
def task_success_handler(sender=None, task_id=None, task=None, **kwargs):
    task_counter.labels(task_name=task.name, status='success').inc()

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, task=None, **kwargs):
    task_counter.labels(task_name=task.name, status='failure').inc()
```

## Resources

- [Celery Documentation](https://docs.celeryq.dev/)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html#best-practices)

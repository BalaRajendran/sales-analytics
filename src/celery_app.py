"""
Celery application configuration.

Background task processing for the Sales Dashboard API.
"""

from celery import Celery
from celery.schedules import crontab

from src.core.config import settings

# Create Celery app
celery_app = Celery(
    "sales_dashboard",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "src.tasks.analytics_tasks",
        "src.tasks.maintenance_tasks",
        "src.tasks.notification_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Result settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
    },
    # Task execution settings
    task_track_started=True,
    task_time_limit=600,  # 10 minutes hard limit
    task_soft_time_limit=540,  # 9 minutes soft limit
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # Refresh materialized views every 5 minutes
    "refresh-realtime-mv": {
        "task": "src.tasks.analytics_tasks.refresh_realtime_materialized_views",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"priority": 9},  # High priority
    },
    # Refresh daily materialized views every hour
    "refresh-daily-mv": {
        "task": "src.tasks.analytics_tasks.refresh_daily_materialized_views",
        "schedule": crontab(minute=0),  # Every hour
        "options": {"priority": 7},
    },
    # Warm dashboard cache every 2 minutes
    "warm-dashboard-cache": {
        "task": "src.tasks.analytics_tasks.warm_dashboard_cache",
        "schedule": crontab(minute="*/2"),  # Every 2 minutes
        "options": {"priority": 8},
    },
    # Update customer segments daily at 2 AM
    "update-customer-segments": {
        "task": "src.tasks.maintenance_tasks.update_customer_segments",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
        "options": {"priority": 5},
    },
    # Update customer lifetime values daily at 3 AM
    "update-customer-ltv": {
        "task": "src.tasks.maintenance_tasks.update_customer_lifetime_values",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
        "options": {"priority": 5},
    },
    # Check low stock daily at 9 AM
    "check-low-stock": {
        "task": "src.tasks.notification_tasks.check_low_stock_products",
        "schedule": crontab(hour=9, minute=0),  # Daily at 9 AM
        "options": {"priority": 4},
    },
    # Clean old partitions weekly on Sunday at 4 AM
    "clean-old-partitions": {
        "task": "src.tasks.maintenance_tasks.clean_old_order_partitions",
        "schedule": crontab(hour=4, minute=0, day_of_week=0),  # Sunday at 4 AM
        "options": {"priority": 3},
    },
    # Generate monthly reports on 1st of month at 6 AM
    "generate-monthly-report": {
        "task": "src.tasks.analytics_tasks.generate_monthly_report",
        "schedule": crontab(hour=6, minute=0, day_of_month=1),  # 1st of month at 6 AM
        "options": {"priority": 6},
    },
}

# Task routes for different queues
celery_app.conf.task_routes = {
    "src.tasks.analytics_tasks.*": {"queue": "analytics"},
    "src.tasks.maintenance_tasks.*": {"queue": "maintenance"},
    "src.tasks.notification_tasks.*": {"queue": "notifications"},
}

# Configure task priorities
celery_app.conf.task_default_priority = 5
celery_app.conf.broker_transport_options = {
    "priority_steps": list(range(10)),  # 0-9 priority levels
}


if __name__ == "__main__":
    celery_app.start()

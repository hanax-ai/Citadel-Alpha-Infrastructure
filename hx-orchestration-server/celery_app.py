"""
Celery Application Configuration

Celery worker configuration for distributed task processing in the 
HX-Orchestration-Server. Handles embedding processing, orchestration 
tasks, and background operations.

Server: hx-orchestration-server (192.168.10.31)
"""

from celery import Celery
from config.settings import get_settings

settings = get_settings()

# Create Celery application
celery_app = Celery(
    "hx_orchestration",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.embedding_tasks",
        "app.tasks.orchestration_tasks",
        "app.tasks.monitoring_tasks",
        "app.tasks.maintenance_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    beat_schedule={
        'health-check': {
            'task': 'app.tasks.monitoring_tasks.health_check',
            'schedule': 60.0,  # Every minute
        },
        'cleanup-old-results': {
            'task': 'app.tasks.maintenance_tasks.cleanup_old_results',
            'schedule': 3600.0,  # Every hour
        },
    }
)

if __name__ == "__main__":
    celery_app.start()

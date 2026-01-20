"""
Celery configuration settings for the Django application.
"""

import os
import environ

env = environ.Env()

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')

CELERY_RESULT_EXTENDED = True
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery task configuration
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

# Task time limits
CELERY_TASK_TIME_LIMIT = 10 * 60  # 10 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 5 * 60  # 5 minutes

# Worker concurrency
CELERY_WORKER_CONCURRENCY = env.int('CELERY_WORKER_CONCURRENCY', default=os.cpu_count() or 1)
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_WORKER_CANCEL_LONG_RUNNING_TASKS_ON_CONNECTION_LOST = True

# Queue settings
DEFAULT_CELERY_QUEUE = 'default'
CELERY_TASK_DEFAULT_QUEUE = DEFAULT_CELERY_QUEUE
CELERY_TASK_QUEUES = {
    DEFAULT_CELERY_QUEUE: {
        'exchange': DEFAULT_CELERY_QUEUE,
        'routing_key': DEFAULT_CELERY_QUEUE,
    },
}

# Task routing
CELERY_TASK_ROUTES = {
    # Define task routing here if needed
}

# Celery beat settings
from celery.schedules import crontab
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_BEAT_SCHEDULE = {
    # Add your periodic tasks here
}

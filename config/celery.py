"""
Celery application configuration for the Django project.

This module sets up the Celery application instance and configures it
to work with Django settings.
"""

import os

from celery import Celery
from celery.signals import worker_process_init

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("config")

# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@worker_process_init.connect(weak=False)
def init_celery_telemetry(**kwargs):
    """Initialize OpenTelemetry in each Celery worker process."""
    from core.telemetry import setup_otlp_logging, setup_telemetry

    setup_telemetry()
    # Django is already loaded in celery workers, so dictConfig has already run.
    # Safe to attach the OTLP logging handler immediately.
    setup_otlp_logging()

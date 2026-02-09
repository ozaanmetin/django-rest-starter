"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# Initialize OpenTelemetry BEFORE Django loads
# This ensures DjangoInstrumentor can properly wrap the WSGI app
from core.telemetry import setup_telemetry

setup_telemetry()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Attach OTLP logging handler AFTER Django's dictConfig has run.
# Django's LOGGING dict (applied during get_wsgi_application) resets root logger
# handlers, so the OTLP handler must be added after that step.
from core.telemetry import setup_otlp_logging

setup_otlp_logging()

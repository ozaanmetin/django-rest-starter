"""
Development settings for the Django application.

This file contains settings specific to the development environment.
It imports from the base settings and overrides certain values to
facilitate local development and debugging.
"""


from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# Development-specific apps
INSTALLED_APPS += [
    'django_extensions',
]

# Add browsable API renderer for development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# Disable ssl redirects for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Cors settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Use console email backend in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Enable sql query logging in development
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
    'propagate': False,
}

# Use local memory cache in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Disable celery eager mode for development (set to False if you dont want synchronous execution)
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_ALWAYS_EAGER', default=True)
# Disable celery eager propagates for development (set to False if you dont want exceptions to propagate)
CELERY_TASK_EAGER_PROPAGATES = env.bool('CELERY_EAGER_PROPAGATES', default=True)
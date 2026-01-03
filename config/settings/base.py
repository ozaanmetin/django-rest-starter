"""
Base settings for the Django application.

This file contains the common settings used across different environments
like development, production, and testing. Environment-specific settings
should be defined in their respective files and import from this base file.

This base settings uses modularized configurations for better organization
and maintainability. If you need to adjust any settings, consider updating the
corresponding module in the `modules` package.

@author Ozan Metin
"""

import environ
from pathlib import Path

from . import modules

# Base directory of application
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Environment
# ----------------------------------------------------------------
env = environ.Env(DEBUG=(bool, False), ALLOWED_HOSTS=(list, []))
environ.Env.read_env(BASE_DIR / '.env')


# Essential settings
# ----------------------------------------------------------------
SECRET_KEY = env.str('DJANGO_SECRET_KEY', default='change-me-in-production')
DEBUG = env.bool('DJANGO_DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])


# Application definition
# ----------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
]

LOCAL_APPS = [

]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# URL and WSGI configuration
# ----------------------------------------------------------------
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# Internationalization
# ----------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Middleware configuration
# ----------------------------------------------------------------
MIDDLEWARE = modules.middleware.MIDDLEWARE


# Template configuration
# ----------------------------------------------------------------
TEMPLATES = modules.templates.TEMPLATES


# Database configuration
# ----------------------------------------------------------------
DATABASES = modules.database.DATABASES
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Password validation
# ----------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = modules.auth.AUTH_PASSWORD_VALIDATORS


# Static and media files
# ----------------------------------------------------------------
STATIC_URL = modules.static.STATIC_URL
STATIC_ROOT = modules.static.STATIC_ROOT
STATICFILES_DIRS = modules.static.STATICFILES_DIRS
MEDIA_URL = modules.static.MEDIA_URL
MEDIA_ROOT = modules.static.MEDIA_ROOT


# Rest Framework configuration
# ----------------------------------------------------------------
REST_FRAMEWORK = modules.rest_framework.REST_FRAMEWORK


# Cache configuration
# ----------------------------------------------------------------
CACHES = modules.cache.CACHES


# Logging configuration
# ----------------------------------------------------------------
LOGGING = modules.logging.LOGGING


# OpenAPI/Swagger configuration
# ----------------------------------------------------------------
SPECTACULAR_SETTINGS = modules.openapi.SPECTACULAR_SETTINGS


# Celery configuration
# ----------------------------------------------------------------
CELERY_BROKER_URL = modules.celery.CELERY_BROKER_URL
CELERY_RESULT_BACKEND = modules.celery.CELERY_RESULT_BACKEND
CELERY_ACCEPT_CONTENT = modules.celery.CELERY_ACCEPT_CONTENT
CELERY_TASK_SERIALIZER = modules.celery.CELERY_TASK_SERIALIZER
CELERY_RESULT_SERIALIZER = modules.celery.CELERY_RESULT_SERIALIZER
CELERY_TIMEZONE = modules.celery.CELERY_TIMEZONE

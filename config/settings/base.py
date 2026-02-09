"""
Base settings for the Django application.

This file contains the common settings used across different environments
like development, production, and testing. Environment-specific settings
should be defined in their respective files and import from this base file.

This base settings uses modularized configurations for better organization
and maintainability. If you need to adjust any settings, consider updating the
corresponding module in the `modules` package.
"""

from pathlib import Path

import environ

# Base directory of application
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Environment
# ----------------------------------------------------------------
env = environ.Env(DEBUG=(bool, False), ALLOWED_HOSTS=(list, []))
environ.Env.read_env(BASE_DIR / ".env")


# Essential settings
# ----------------------------------------------------------------
SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="change-me-in-production")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


# Application definition
# ----------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    # rest framework
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    # cleanup
    "django_cleanup.apps.CleanupConfig",
    # admin filtering
    "admin_auto_filters",
    "rangefilter",
    # django filter backend
    "django_filters",
    "corsheaders",
    "drf_spectacular",
    # celery
    "django_celery_results",
    "django_celery_beat",
]

LOCAL_APPS = [
    "core",
    "app.accounts",
    "app.authentication",
    "app.authorization",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# URL and WSGI configuration
# ----------------------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


# Internationalization
# ----------------------------------------------------------------
LANGUAGE_CODE = env("LANGUAGE_CODE", default="tr")
LANGUAGES = [
    ("en", "English"),
    ("tr", "Turkish"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = env("TIME_ZONE", default="Europe/Istanbul")
USE_I18N = True
USE_L10N = True
USE_TZ = True

if USE_TZ:
    # Set Celery timezone to match Django timezone if timezone support is enabled
    CELERY_TIMEZONE = TIME_ZONE


# Import all settings from modules
# ----------------------------------------------------------------
# This automatically imports all uppercase variables from each module
# Much cleaner than importing each setting individually

# Middleware
# Authentication & Security
from .modules.auth import *

# Cache
from .modules.cache import *

# Celery
from .modules.celery import *

# CORS
from .modules.cors import *

# Database
from .modules.database import *

# Logging
from .modules.logging import *
from .modules.middleware import *

# OpenAPI/Swagger
from .modules.openapi import *

# OpenTelemetry
from .modules.otel import *

# REST Framework
from .modules.rest_framework import *

# Security
from .modules.security import *

# Monitoring
from .modules.sentry import *

# Static files
from .modules.static import *

# Templates
from .modules.templates import *

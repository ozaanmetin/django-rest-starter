from .base import *

# Production settings for the Django application.
DEBUG = False
SECRET_KEY = env.str('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Security settings (override base security module for production)
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session & CSRF cookies must be secure in production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Data upload limits can be configured via environment
DATA_UPLOAD_MAX_MEMORY_SIZE = env.int('DATA_UPLOAD_MAX_MEMORY_SIZE', default=5242880)  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int('FILE_UPLOAD_MAX_MEMORY_SIZE', default=5242880)  # 5MB

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@example.com')


# Cache configuration for production
CACHES["default"]["OPTIONS"]["IGNORE_EXCEPTIONS"] = True


# Static files storage for production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'


# Ensure critical settings are set
if not SECRET_KEY:
    raise ValueError('SECRET_KEY must be set in production')

if not ALLOWED_HOSTS:
    raise ValueError('ALLOWED_HOSTS must be set in production')

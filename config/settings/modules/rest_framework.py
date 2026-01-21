"""
Django REST Framework settings for the application.
"""

import environ

env = environ.Env()

REST_FRAMEWORK = {
    # Default renderer classes
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],

    # Default parser classes
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],

    # Default authentication and permission classes
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    # Exception handler
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',

    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardPageNumberPagination',
    'PAGE_SIZE': 10,

    # Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    # Throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },

    # Security (For private files)
    'UPLOADED_FILES_USE_URL': False,

    # Openapi schema
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Set NUM_PROXIES if behind a load balancer
if env.bool('USE_PROXY', default=False):
    REST_FRAMEWORK['NUM_PROXIES'] = env.int('NUM_PROXIES', default=1)

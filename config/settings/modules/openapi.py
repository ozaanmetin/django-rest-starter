"""
OpenAPI (drf-spectacular) settings for the Django application.
"""

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django REST API',
    'DESCRIPTION': 'API documentation for Django REST project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1',
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'ENUM_NAME_OVERRIDES': {},
    'POSTPROCESSING_HOOKS': [],
    'PREPROCESSING_HOOKS': [],
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'SERVE_AUTHENTICATION': None,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'REDOC_SETTINGS': {
        'LAZY_RENDERING': True,
    },
    'SERVE_PUBLIC': True,
    'SCHEMA_COERCE_METHOD_NAMES': {
        'list': 'list',
        'create': 'create',
        'retrieve': 'retrieve',
        'update': 'update',
        'partial_update': 'partial_update',
        'destroy': 'destroy',
    },
}

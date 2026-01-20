"""
Cache settings for the Django application.
"""

import environ

env = environ.Env()

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.str("REDIS_URL", default="redis://redis:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": env.int("REDIS_MAX_CONNECTIONS", default=50),
            },
            "SOCKET_CONNECT_TIMEOUT": env.int("REDIS_SOCKET_CONNECT_TIMEOUT", default=2),
            "SOCKET_TIMEOUT": env.int("REDIS_SOCKET_TIMEOUT", default=2),
        },
        "KEY_PREFIX": env.str('CACHE_KEY_PREFIX', default='django_rest'),
        "TIMEOUT": env.int("CACHE_DEFAULT_TIMEOUT", default=300),
    },
}

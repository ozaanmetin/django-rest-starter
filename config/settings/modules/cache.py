import environ

env = environ.Env()

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "LOCATION": env.str("REDIS_URL", default="redis://redis:6379/0"),
    },
}

CACHES['default']['KEY_PREFIX'] = env('CACHE_KEY_PREFIX', default='django_rest')

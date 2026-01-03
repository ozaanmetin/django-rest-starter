import environ

env = environ.Env()

DATABASES = {
    "default": {
        # Database connection settings
        "ENGINE": env.str("DB_ENGINE"),
        "NAME": env.str("DB_NAME"),
        "USER": env.str("DB_USER"),
        "PASSWORD": env.str("DB_PASSWORD"),
        "HOST": env.str("DB_HOST"),
        "PORT": env.str("DB_PORT"),
        # Connection pooling
        "CONN_MAX_AGE": env.int("DB_CONN_MAX_AGE", 600),
        # Django 4.1+ persistent connection health check
        "CONN_HEALTH_CHECKS": env.bool("DB_CONN_HEALTH_CHECKS", True),
        # Additional options
        "OPTIONS": {
            "client_encoding": "UTF8",
            "connect_timeout": env.int("DB_CONNECT_TIMEOUT", 10),
        },
    }
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

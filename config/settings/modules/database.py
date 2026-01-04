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
        # Wrap each request in a transaction (reduces performance slightly)
        "ATOMIC_REQUESTS": env.bool("DB_ATOMIC_REQUESTS", default=False),
        # Additional options
        "OPTIONS": {
            "client_encoding": "UTF8",
            "connect_timeout": env.int("DB_CONNECT_TIMEOUT", 10),
            "options": f"-c statement_timeout={env.int('DB_STATEMENT_TIMEOUT', 30000)}",
        },
    }
}

# Enable SSL for production
if env.bool("DB_SSL_REQUIRED", default=False):
    DATABASES["default"]["OPTIONS"]["sslmode"] = "require"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
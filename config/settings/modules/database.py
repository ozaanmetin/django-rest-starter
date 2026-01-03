import environ

env = environ.Env()

DATABASES = {
    'default': env.db_url(
        'DATABASE_URL',
        default=f"postgresql://{env('DB_USER', default='postgres')}:"
                f"{env('DB_PASSWORD', default='')}@"
                f"{env('DB_HOST', default='localhost')}:"
                f"{env('DB_PORT', default='5432')}/"
                f"{env('DB_NAME', default='django_rest_db')}"
    )
}

DATABASES['default']['CONN_MAX_AGE'] = env.int('DB_CONN_MAX_AGE', default=600)
DATABASES['default'].setdefault('OPTIONS', {})
DATABASES['default']['OPTIONS']['connect_timeout'] = 10

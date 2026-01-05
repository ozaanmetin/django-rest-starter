"""
Monitoring settings for the Django application.

@author Ozan Metin
"""

import environ

env = environ.Env()

# Sentry Configuration (Error tracking)
SENTRY_ENABLED = env.bool('SENTRY_ENABLED', default=False)

if SENTRY_ENABLED:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=env.str('SENTRY_DSN'),
        environment=env.str('SENTRY_ENVIRONMENT', default='production'),
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=env.float('SENTRY_TRACES_SAMPLE_RATE', default=0.1),
        profiles_sample_rate=env.float('SENTRY_PROFILES_SAMPLE_RATE', default=0.1),
        send_default_pii=False,
        max_breadcrumbs=50,
    )

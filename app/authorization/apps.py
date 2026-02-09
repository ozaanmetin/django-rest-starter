from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthorizationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.authorization"
    verbose_name = _("01.1 - Authorization")

    def ready(self):
        from django.contrib.auth.management import create_permissions as django_create_permissions
        from django.db.models.signals import post_migrate

        from .models.role.migration import create_permissions as custom_create_permissions

        # Disconnect Django's default permission creator
        post_migrate.disconnect(
            django_create_permissions,
            dispatch_uid="django.contrib.auth.management.create_permissions",
        )

        # Connect our custom permission creator
        post_migrate.connect(
            custom_create_permissions,
            dispatch_uid="custom_create_permissions",
        )

        # Import signals to register them
        from . import signals  # noqa: F401

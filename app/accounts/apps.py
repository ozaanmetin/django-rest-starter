from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.accounts"
    verbose_name = _("01.0 - Accounts")

    def ready(self):
        from . import signals  # noqa: F401

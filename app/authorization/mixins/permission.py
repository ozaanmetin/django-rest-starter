"""
Custom permissions mixin for User model.

This mixin provides role and permission fields that work with
our custom Role and Permission models.

All permission checks delegate to the authentication backend (AuthBackend).

Why these methods exist:
- Django Admin calls user.has_perm() and user.has_module_perms()
- DRF permission classes call user.has_perm()
- Templates use {% if user.has_perm 'x' %}
- These methods MUST exist on User model, they delegate to AuthBackend
"""

from collections.abc import Iterable

from django.contrib.auth import get_backends
from django.db import models
from django.utils.translation import gettext_lazy as _


def _get_backend():
    """Get the first backend that has permission methods."""
    for backend in get_backends():
        if hasattr(backend, "has_perm"):
            return backend
    return None


class RolePermissionsMixin(models.Model):
    """
    Mixin that adds role and permission fields to User model.

    Replaces Django's PermissionsMixin to work with our custom Role/Permission models.
    Permission methods delegate to AuthBackend - this mixin just provides the interface.
    """

    roles = models.ManyToManyField(
        "authorization.Role",
        verbose_name=_("roller"),
        blank=True,
        help_text=_("Kullanıcının ait olduğu roller."),
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "authorization.Permission",
        verbose_name=_("kullanıcı yetkileri"),
        blank=True,
        help_text=_("Bu kullanıcıya özel yetkiler."),
        related_name="user_set",
        related_query_name="user",
    )
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_("Kullanıcının tüm izinlere sahip olduğunu belirtir."),
    )

    class Meta:
        abstract = True

    # Role Helpers - Convenience methods for role management

    def add_role(self, role) -> None:
        self.roles.add(role)

    def remove_role(self, role) -> None:
        self.roles.remove(role)

    def has_role(self, codename: str) -> bool:
        return self.roles.filter(codename=codename, is_active=True).exists()

    def get_role_codenames(self) -> list[str]:
        return list(self.roles.filter(is_active=True).values_list("codename", flat=True))

    # Permission Interface - Required by Django Admin, DRF, Templates
    # These just delegate to AuthBackend, but MUST exist on User model

    def has_perm(self, perm: str, obj=None) -> bool:
        """Required by: Django Admin, DRF permissions, templates."""
        if self.can_authenticate and self.is_superuser:
            return True
        backend = _get_backend()
        return backend.has_perm(self, perm, obj) if backend else False

    def has_perms(self, perm_list: Iterable[str], obj=None) -> bool:
        """Required by: Django Admin bulk permission checks."""
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label: str) -> bool:
        """Required by: Django Admin sidebar visibility."""
        if self.can_authenticate and self.is_superuser:
            return True
        backend = _get_backend()
        return backend.has_module_perms(self, app_label) if backend else False

from django.db import models
from django.utils.translation import gettext_lazy as _

from pkg.django.models import IsActiveModel, TimestampedModel

from .manager import PermissionManager, RoleManager


class Permission(TimestampedModel):
    """
    Custom Permission model with multi-language name support.

    Codename format: app_label.model_name.action
    Examples: assets.camera.view, authorization.role.delete
    """

    codename = models.CharField(_("Kod"), max_length=255, unique=True)
    name = models.JSONField(
        _("Yetki Adı"),
        help_text=_('Farklı dillerde yetki ismi. Örn: {"en": "Can View", "tr": "Görüntüleyebilir"}'),
    )
    description = models.TextField(_("Açıklama"), blank=True, default="")

    objects = PermissionManager()

    class Meta:
        db_table = "permissions"
        ordering = ["codename"]
        verbose_name = _("Yetki")
        verbose_name_plural = _("02.1 - Yetkiler")

    def __str__(self) -> str:
        return self.codename

    def get_name(self, lang: str = "en") -> str:
        """Get permission name for the given language."""
        if isinstance(self.name, dict):
            return self.name.get(lang, self.name.get("en", self.codename))
        return str(self.name)


class Role(IsActiveModel, TimestampedModel):
    """
    Custom Role model for role-based access control (RBAC).

    Cache invalidation is handled via post_save/post_delete hooks.
    """

    name = models.JSONField(
        _("İsim"),
        help_text=_('Rol ismi farklı dillerde. Örn: {"en": "Admin", "tr": "Yönetici"}'),
    )
    codename = models.CharField(_("Kod"), max_length=150, unique=True)
    description = models.TextField(_("Açıklama"), blank=True, default="")
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
        related_name="roles",
    )

    objects = RoleManager()

    class Meta:
        db_table = "roles"
        ordering = ["codename"]
        verbose_name = _("Rol")
        verbose_name_plural = _("02.0 - Roller")

    def __str__(self) -> str:
        return self.codename

    def get_name(self, lang: str = "en") -> str:
        """Get role name for the given language."""
        if isinstance(self.name, dict):
            return self.name.get(lang, self.name.get("en", self.codename))
        return str(self.name)

    def get_permission_codenames(self) -> list[str]:
        """Get list of permission codenames for this role."""
        return list(self.permissions.values_list("codename", flat=True))

    def _invalidate_users_cache(self):
        """Invalidate permission cache for all users with this role."""
        from app.authorization.caches.permissions import user_permissions_cache

        return user_permissions_cache.invalidate_role_users(self)

    def post_save(self, *args, **kwargs):
        """Invalidate cache for users when role is updated (e.g., deactivated)."""
        self._invalidate_users_cache()

    def pre_delete(self, *args, **kwargs):
        """Store user IDs before deletion since M2M will be cleared."""
        self._user_ids_for_cache = list(self.user_set.values_list("id", flat=True))

    def post_delete(self, *args, **kwargs):
        """Invalidate cache for users who had this role."""
        from app.authorization.caches.permissions import user_permissions_cache

        for user_id in self._user_ids_for_cache:
            user_permissions_cache.invalidate_user(user_id)

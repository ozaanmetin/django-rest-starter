"""
Custom authentication backend for Role-based permission system.

Which overrides Django's default ModelBackend to work with our
custom Role and Permission models.

Method names and approaches must be compatible with Django's auth system.
So make minimal changes to the original ModelBackend logic.

Performance:
    - Uses Redis cache for permissions (5 min TTL)
    - Falls back to request-level cache if Redis unavailable
    - Single cache lookup instead of multiple DB queries
"""

from django.contrib.auth.backends import ModelBackend


class AuthBackend(ModelBackend):
    """
    Authentication backend for custom Role/Permission models.

    Authentication (login) is inherited from ModelBackend unchanged.
    Only permission-related methods are overridden to work with our
    custom Permission model (no content_type, just codename).

    Permission codename format: app_label.model_name.action

    Caching Strategy:
        1. Check Redis cache first (shared across requests)
        2. If miss, query DB and cache result
        3. Also cache on user instance for same-request reuse
    """

    # Authentication

    def user_can_authenticate(self, user):
        """Check if user is allowed to authenticate."""
        return getattr(user, "can_authenticate", True)

    # Permission Cache

    def _get_cached_permissions(self, user_obj):
        """
        Get permissions from cache (Redis) or build from database.

        Returns UserPermissionsData dict with all permission info.
        """
        from app.authorization.caches.permissions import user_permissions_cache

        return user_permissions_cache.get_or_build(user_obj)

    # Public Permission API (sync)

    def get_user_permissions(self, user_obj, obj=None):
        """Return permission codenames directly assigned to user."""
        if not self.user_can_authenticate(user_obj) or user_obj.is_anonymous or obj is not None:
            return set()

        if not hasattr(user_obj, "_user_perm_cache"):
            data = self._get_cached_permissions(user_obj)
            user_obj._user_perm_cache = set(data["user_permissions"])
        return user_obj._user_perm_cache

    def get_group_permissions(self, user_obj, obj=None):
        """Return permission codenames from user's roles."""
        if not self.user_can_authenticate(user_obj) or user_obj.is_anonymous or obj is not None:
            return set()

        if not hasattr(user_obj, "_role_perm_cache"):
            data = self._get_cached_permissions(user_obj)
            user_obj._role_perm_cache = set(data["role_permissions"])
        return user_obj._role_perm_cache

    def get_all_permissions(self, user_obj, obj=None):
        """Return all permission codenames for user (direct + from roles)."""
        if not self.user_can_authenticate(user_obj) or user_obj.is_anonymous or obj is not None:
            return set()

        if not hasattr(user_obj, "_perm_cache"):
            # Superuser gets all permissions
            if user_obj.is_superuser:
                from app.authorization.models import Permission

                user_obj._perm_cache = set(Permission.objects.values_list("codename", flat=True))
            else:
                data = self._get_cached_permissions(user_obj)
                user_obj._perm_cache = set(data["all_permissions"])
        return user_obj._perm_cache

    # Permission Check (sync)

    def has_perm(self, user_obj, perm, obj=None):
        """Check if user has a specific permission."""
        if not self.user_can_authenticate(user_obj):
            return False
        if user_obj.is_superuser:
            return True
        return perm in self.get_all_permissions(user_obj, obj)

    def has_module_perms(self, user_obj, app_label):
        """Check if user has any permissions for the given app/module."""
        if not self.user_can_authenticate(user_obj):
            return False
        if user_obj.is_superuser:
            return True
        return any(perm.startswith(f"{app_label}.") for perm in self.get_all_permissions(user_obj))

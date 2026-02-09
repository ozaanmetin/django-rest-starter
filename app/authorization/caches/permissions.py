"""
Cache service for user permissions.

Caches permission codenames per user in Redis to avoid
repeated database queries on every request.
"""

from typing import TypedDict
from uuid import UUID

from core.cache import CacheService


class UserPermissionsData(TypedDict):
    """Cached permission data for a user."""

    user_permissions: list[str]  # Direct user permissions
    role_permissions: list[str]  # Permissions from roles
    all_permissions: list[str]  # Combined unique permissions
    role_codenames: list[str]  # Active role codenames


class UserPermissionsCacheService(CacheService):
    """
    Cache service for user permissions.

    Caches all permission-related data for a user to minimize
    database queries during authorization checks.

    Keys:
        - permissions:v1:user:{user_id} -> UserPermissionsData

    Cache is invalidated when:
        - User's roles change
        - User's direct permissions change
        - Role's permissions change
    """

    NAMESPACE = "permissions"
    VERSION = 1
    DEFAULT_TIMEOUT = 60 * 5  # 5 minutes

    def _get_key(self, *parts: str) -> str:
        """Build cache key."""
        return self.key_builder(self.NAMESPACE, self.VERSION).add(*parts).build()

    def get_by_user_id(self, user_id: UUID | str) -> UserPermissionsData | None:
        """Get cached permissions for a user."""
        key = self._get_key("user", str(user_id))
        return self.backend.get(key)

    def set_for_user(
        self,
        user_id: UUID | str,
        data: UserPermissionsData,
        timeout: int | None = None,
    ) -> bool:
        """Cache permissions for a user."""
        key = self._get_key("user", str(user_id))
        return self.backend.set(key, data, timeout or self.DEFAULT_TIMEOUT)

    def build_and_cache(self, user) -> UserPermissionsData:
        """
        Build permission data from database and cache it.

        Args:
            user: User model instance

        Returns:
            UserPermissionsData with all permission info
        """
        from app.authorization.models import Permission

        # Get user's direct permissions
        user_perms = list(user.user_permissions.values_list("codename", flat=True))

        # Get permissions from active roles
        active_roles = user.roles.filter(is_active=True)
        role_codenames = list(active_roles.values_list("codename", flat=True))
        role_perms = list(
            Permission.objects.filter(roles__in=active_roles).distinct().values_list("codename", flat=True)
        )

        # Combine and deduplicate
        all_perms = list(set(user_perms) | set(role_perms))

        data: UserPermissionsData = {
            "user_permissions": user_perms,
            "role_permissions": role_perms,
            "all_permissions": all_perms,
            "role_codenames": role_codenames,
        }

        # Cache it
        self.set_for_user(user.id, data)

        return data

    def get_or_build(self, user) -> UserPermissionsData:
        """
        Get cached permissions or build from database.

        This is the main entry point for permission lookups.
        """
        # Try cache first
        cached = self.get_by_user_id(user.id)
        if cached is not None:
            print("Cache hit for user permissions:", user.id)
            return cached

        print("Cache miss for user permissions:", user.id)
        # Build from database and cache
        return self.build_and_cache(user)

    def invalidate_user(self, user_id: UUID | str) -> bool:
        """Invalidate cache for a specific user."""
        key = self._get_key("user", str(user_id))
        return self.backend.delete(key)

    def invalidate_role_users(self, role) -> int:
        """
        Invalidate cache for all users with a specific role.

        Call this when a role's permissions change.
        """
        count = 0
        for user_id in role.user_set.values_list("id", flat=True):
            if self.invalidate_user(user_id):
                count += 1
        return count

    def invalidate_all(self) -> int:
        """Invalidate all permission caches."""
        pattern = self.key_builder.pattern(self.NAMESPACE, self.VERSION, "*")
        return self.backend.clear_pattern(pattern)


user_permissions_cache = UserPermissionsCacheService()

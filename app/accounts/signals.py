"""
User M2M signals for cache invalidation.

This module is imported in AccountsConfig.ready() to ensure all models are loaded.
"""

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from app.authorization.caches.permissions import user_permissions_cache

from .models.user.model import User


@receiver(m2m_changed, sender=User.roles.through)
def invalidate_on_user_roles_change(sender, instance, action, **kwargs):
    """Invalidate cache when a user's roles change."""
    if action in ("post_add", "post_remove", "post_clear"):
        user_permissions_cache.invalidate(instance)


@receiver(m2m_changed, sender=User.user_permissions.through)
def invalidate_on_user_permissions_change(sender, instance, action, **kwargs):
    """Invalidate cache when a user's direct permissions change."""
    if action in ("post_add", "post_remove", "post_clear"):
        user_permissions_cache.invalidate(instance)

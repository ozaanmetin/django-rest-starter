"""Django signals for M2M cache invalidation.

M2M changes cannot be handled via model hooks (pre_save/post_save),
so we use Django signals specifically for M2M relationships.

Non-M2M cache invalidation is handled in model's post_save/post_delete hooks.

Note: This module is imported in AppConfig.ready() to ensure all models are loaded.
"""

import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from app.authorization.caches.permissions import user_permissions_cache
from app.authorization.models import Role

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=Role.permissions.through)
def invalidate_on_role_permissions_change(sender, instance, action, **kwargs):
    """Invalidate cache when a role's permissions change."""
    if action in ("post_add", "post_remove", "post_clear"):
        user_permissions_cache.invalidate_role_users(instance)

from django.contrib import admin
from django.contrib.auth.models import Group

from .user import UserAdmin

# Remove Group from admin (we don't use Django's built-in permissions)
admin.site.unregister(Group)

__all__ = ["UserAdmin"]

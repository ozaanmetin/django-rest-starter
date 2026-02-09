"""
Custom admin classes with permission support for our RBAC system.

Django admin uses permission format: app_label.action_modelname (e.g., places.view_location)
Our RBAC uses format: app_label.model_name.action (e.g., places.location.view)

This module provides admin classes that translate between these formats.
"""

from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base ModelAdmin that uses our custom permission format.

    Permission codename format: app_label.model_name.action
    """

    def _get_permission_codename(self, action: str) -> str:
        """Get permission codename in our format: app_label.model_name.action"""
        opts = self.model._meta
        return f"{opts.app_label}.{opts.model_name}.{action}"

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("view"))

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("add"))

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("change"))

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("delete"))

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.has_module_perms(self.model._meta.app_label)


class BaseTabularInline(admin.TabularInline):
    """Base TabularInline with RBAC permission support."""

    def _get_permission_codename(self, action: str) -> str:
        opts = self.model._meta
        return f"{opts.app_label}.{opts.model_name}.{action}"

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("view"))

    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("add"))

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("change"))

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("delete"))


class BaseStackedInline(admin.StackedInline):
    """Base StackedInline with RBAC permission support."""

    def _get_permission_codename(self, action: str) -> str:
        opts = self.model._meta
        return f"{opts.app_label}.{opts.model_name}.{action}"

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("view"))

    def has_add_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("add"))

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("change"))

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return request.user.has_perm(self._get_permission_codename("delete"))

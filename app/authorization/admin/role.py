from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from app.authorization.models import Permission, Role
from core.admin import BaseModelAdmin


@admin.register(Role)
class RoleAdmin(BaseModelAdmin):
    list_display = ("codename", "get_name_display", "permission_count", "user_count", "is_active")
    list_filter = ("is_active",)
    search_fields = ("codename", "name")
    ordering = ("codename",)
    filter_horizontal = ("permissions",)

    def get_name_display(self, obj):
        return obj.get_name("tr")

    def permission_count(self, obj):
        return obj.permissions.count()

    def user_count(self, obj):
        return obj.user_set.count()

    get_name_display.short_description = _("Ad")
    permission_count.short_description = _("Yetki Sayısı")
    user_count.short_description = _("Kullanıcı Sayısı")


@admin.register(Permission)
class PermissionAdmin(BaseModelAdmin):
    list_display = ("codename", "get_name_display", "created_at")
    search_fields = ("codename", "name")
    ordering = ("codename",)

    def get_name_display(self, obj):
        return obj.get_name("tr")

    get_name_display.short_description = _("Ad")

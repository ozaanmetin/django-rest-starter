from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateTimeRangeFilterBuilder

from app.accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""

    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "is_active",
        "created_at",
        "updated_at"
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        ("created_at", DateTimeRangeFilterBuilder()),
        ("updated_at", DateTimeRangeFilterBuilder()),
        ("date_joined", DateTimeRangeFilterBuilder()),
        ("last_login", DateTimeRangeFilterBuilder()),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-created_at",)
    filter_horizontal = []

    fieldsets = (
        (("Login Credentials"), {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login", "created_at", "updated_at")

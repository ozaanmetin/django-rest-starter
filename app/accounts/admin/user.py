from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateTimeRangeFilterBuilder

from app.accounts.models import User
from app.authorization.models import Permission, Role
from core.admin import BaseModelAdmin


class UserChangeForm(forms.ModelForm):
    """Form for changing users in admin."""

    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this user's password, "
            'but you can change the password using <a href="../password/">this form</a>.'
        ),
    )
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(_("Roller"), False),
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(_("Yetkiler"), False),
    )

    class Meta:
        model = User
        fields = "__all__"


class UserCreationForm(forms.ModelForm):
    """Form for creating new users in admin."""

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(BaseModelAdmin):
    """Admin configuration for User model."""

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        ("created_at", DateTimeRangeFilterBuilder(_("Creation Date"))),
        ("updated_at", DateTimeRangeFilterBuilder(_("Update Date"))),
        ("date_joined", DateTimeRangeFilterBuilder(_("Date Joined"))),
        ("last_login", DateTimeRangeFilterBuilder(_("Last Login"))),
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-created_at",)
    filter_horizontal = ("roles", "user_permissions")

    fieldsets = (
        (_("Login Credentials"), {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {"fields": ("roles", "user_permissions", "is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "first_name", "last_name", "password1", "password2")}),
    )

    readonly_fields = ("date_joined", "last_login", "created_at", "updated_at")

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs["form"] = self.add_form
        return super().get_form(request, obj, **kwargs)

"""
User model which will be used for authentication for application.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from pkg.django.models import IsActiveModel, TimestampedModel, UUIDPrimaryKeyModel

from .manager import UserManager


class User(UUIDPrimaryKeyModel, IsActiveModel, TimestampedModel, PermissionsMixin, AbstractBaseUser):
    """
    Custom User model with UUID primary key.
    """

    # user fields
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    # fields for permissions
    is_staff = models.BooleanField(
        default=False,
        help_text=_("Designates whether the user can log into this admin site"),
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text=_("Designates that this user has all permissions without explicitly assigning them"),
    )

    # timestamps
    date_joined = models.DateTimeField(_("Date joined"), auto_now_add=True)
    last_login = models.DateTimeField(_("Last login"), null=True, blank=True)

    # manager
    objects: UserManager = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]

    class Meta:
        db_table = "accounts_users"
        ordering = ["-created_at"]
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return str(self.id)

    def get_full_name(self) -> str:
        """Return the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def can_sign_in(self) -> bool:
        return self.is_active

"""
User model which will be used for authentication for application.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from app.authorization.mixins import RolePermissionsMixin
from pkg.django.models import IsActiveModel, TimestampedModel, UUIDPrimaryKeyModel

from .manager import UserManager


class User(UUIDPrimaryKeyModel, IsActiveModel, TimestampedModel, RolePermissionsMixin, AbstractBaseUser):
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
        help_text=_("Kullanıcının admin ekranına erişim izni var mı?"),
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
        db_table = "users"
        ordering = ["-created_at"]
        verbose_name = _("Kullanıcı")
        verbose_name_plural = _("01.1 - Kullanıcılar")

    def __str__(self) -> str:
        return str(self.id)

    def get_full_name(self) -> str:
        """Return the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def can_authenticate(self) -> bool:
        return self.is_active

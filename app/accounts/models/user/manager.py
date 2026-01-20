"""Custom Manager for User model."""

from django.contrib.auth.models import BaseUserManager
from pkg.django.managers import TimestampedManager, IsActiveManager

from .queryset import UserQuerySet


class UserManager(BaseUserManager, TimestampedManager, IsActiveManager):
    """Manager for User model with email-based authentication."""

    def get_queryset(self) -> UserQuerySet:
        return UserQuerySet(self.model, using=self._db)

    def create_user(self, email: str, first_name: str, last_name: str, password: str | None = None, **extra_fields):
        """Create and return a regular user with the given email and password."""
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, first_name: str, last_name: str, password: str | None = None, **extra_fields):
        """Create and return a superuser with the given email and password."""
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        return self.create_user(email, first_name, last_name, password, **extra_fields)

    def by_email(self, email: str):
        """Filter users by email (case-insensitive)."""
        return self.get_queryset().by_email(email)

    def staff(self):
        """Filter to staff users only."""
        return self.get_queryset().staff()

    def superusers(self):
        """Filter to superusers only."""
        return self.get_queryset().superusers()


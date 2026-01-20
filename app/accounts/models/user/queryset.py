"""Custom QuerySet for User model."""

from pkg.django.querysets import IsActiveQuerySet, TimestampedQuerySet


class UserQuerySet(TimestampedQuerySet, IsActiveQuerySet):
    """QuerySet for User model with active/inactive and timestamp support."""

    def by_email(self, email: str):
        """Filter users by email (case-insensitive)."""
        return self.filter(email__iexact=email)

    def staff(self):
        """Filter to staff users only."""
        return self.filter(is_staff=True)

    def superusers(self):
        """Filter to superusers only."""
        return self.filter(is_superuser=True)
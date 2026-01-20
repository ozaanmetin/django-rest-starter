"""Custom QuerySet classes for abstract base models."""

from django.db import models
from django.utils import timezone


class TimestampedQuerySet(models.QuerySet):
    """QuerySet that automatically sets updated_at on bulk updates."""

    def update(self, **kwargs):
        """Sets updated_at to current time before performing bulk update."""
        kwargs["updated_at"] = models.functions.Now()
        return super().update(**kwargs)


class IsActiveQuerySet(models.QuerySet):
    """QuerySet with active/inactive filtering methods."""

    def active(self):
        """Filters to records where is_active=True."""
        return self.filter(is_active=True)

    def inactive(self):
        """Filters to records where is_active=False."""
        return self.filter(is_active=False)


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet that supports soft delete operations on bulk queries."""

    def delete(self):
        """Soft deletes all records by setting deleted_at timestamp."""
        return self.update(deleted_at=timezone.now())

    def restore(self):
        """Restores soft-deleted records by clearing deleted_at."""
        return self.update(deleted_at=None)

    def hard_delete(self):
        """Permanently removes records from the database."""
        return super().delete()

    def deleted(self):
        """Filters to only soft-deleted records."""
        return self.filter(deleted_at__isnull=False)

    def not_deleted(self):
        """Filters to only non-deleted records."""
        return self.filter(deleted_at__isnull=True)

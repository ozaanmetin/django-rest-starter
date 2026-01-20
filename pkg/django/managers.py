"""Custom model managers for abstract base models."""

from django.db import models

from . import querysets


class TimestampedManager(models.Manager):
    """Manager for TimestampedModel that ensures updated_at is set on bulk updates."""

    queryset = querysets.TimestampedQuerySet

    def get_queryset(self) -> querysets.TimestampedQuerySet:
        return querysets.TimestampedQuerySet(self.model, using=self._db)


class IsActiveManager(models.Manager):
    """Manager that provides .active() and .inactive() filtering shortcuts."""

    queryset = querysets.IsActiveQuerySet

    def get_queryset(self) -> querysets.IsActiveQuerySet:
        return querysets.IsActiveQuerySet(self.model, using=self._db)

    def active(self):
        """Returns queryset filtered to is_active=True."""
        return self.get_queryset().active()

    def inactive(self):
        """Returns queryset filtered to is_active=False."""
        return self.get_queryset().inactive()


class SoftDeleteManager(models.Manager):
    """
    Manager for SoftDeleteModel that excludes deleted records by default.

    Use .with_deleted() to include all records, or .deleted() for only deleted ones.
    """

    def _queryset(self):
        """Returns the base queryset without any filtering applied."""
        return querysets.SoftDeleteQuerySet(self.model, using=self._db)

    def get_queryset(self):
        """Returns queryset excluding soft-deleted records."""
        return self._queryset().not_deleted()

    def deleted(self):
        """Returns queryset of only soft-deleted records."""
        return self._queryset().deleted()

    def not_deleted(self):
        """Returns queryset excluding soft-deleted records."""
        return self._queryset().not_deleted()

    def with_deleted(self):
        """Returns queryset including all records (deleted and non-deleted)."""
        return self._queryset()

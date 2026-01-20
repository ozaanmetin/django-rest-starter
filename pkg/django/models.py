"""Abstract base models for common patterns."""

from django.db import models
from django.utils import timezone

from ..utils.uuid import uuid7
from . import managers


class TimestampedModel(models.Model):
    """
    Abstract model that auto-manages created_at and updated_at timestamps.

    Automatically sets updated_at on every save, even when using update_fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    objects: managers.TimestampedManager = managers.TimestampedManager()

    def save(self, *args, **kwargs):
        """Ensures updated_at is included in update_fields if specified."""
        update_fields = kwargs.get("update_fields", None)
        if update_fields:
            kwargs["update_fields"] = set(update_fields).union({"updated_at"})
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class IsActiveModel(models.Model):
    """
    Abstract model with an is_active boolean field.

    Provides .active() and .inactive() queryset methods via IsActiveManager.
    """

    is_active = models.BooleanField(default=True)
    objects: managers.IsActiveManager = managers.IsActiveManager()

    class Meta:
        abstract = True


class UUIDPrimaryKeyModel(models.Model):
    """
    Abstract model that uses UUID7 as the primary key instead of auto-increment.

    UUID7 is time-sortable, making it suitable for distributed systems while
    maintaining index efficiency.
    """

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    def get_id_repr(self):
        return str(self.id)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract model that adds a unique UUID7 field alongside the default PK.

    Useful when you need a public identifier separate from the internal ID.
    """

    uuid = models.UUIDField(default=uuid7, editable=False, unique=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract model that marks records as deleted instead of removing them.

    Records are filtered out by default. Use .with_deleted() to include them.
    """

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = managers.SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Marks the record as deleted by setting deleted_at timestamp."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, *args, **kwargs):
        """Permanently removes the record from the database."""
        super().delete(*args, **kwargs)

    def restore(self, *args, **kwargs):
        """Restores a soft-deleted record by clearing deleted_at."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

"""Abstract base models for common patterns."""

from django.db import models
from django.utils import timezone

from ..utils.uuid import uuid7
from . import managers


class BaseModel(models.Model):
    """
    Abstract model with lifecycle hooks for save and delete operations.

    Override these methods in subclasses to add custom behavior:
        - pre_save(): Called before save
        - post_save(): Called after save
        - pre_delete(): Called before delete
        - post_delete(): Called after delete
    """

    # If True in migrations, default permissions (add, change, delete, view) will be created.
    # Disable in model if not desired.
    CREATE_DEFAULT_PERMISSIONS = True

    class Meta:
        abstract = True
        default_permissions = ()  # Disable Django's auto permission creation

    def pre_save(self, *args, **kwargs):
        """Hook called before save. Override in subclass."""
        pass

    def post_save(self, *args, **kwargs):
        """Hook called after save. Override in subclass."""
        pass

    def pre_delete(self, *args, **kwargs):
        """Hook called before delete. Override in subclass."""
        pass

    def post_delete(self, *args, **kwargs):
        """Hook called after delete. Override in subclass."""
        pass

    def save(self, *args, **kwargs):
        self.pre_save(*args, **kwargs)
        super().save(*args, **kwargs)
        self.post_save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.pre_delete(*args, **kwargs)
        result = super().delete(*args, **kwargs)
        self.post_delete(*args, **kwargs)
        return result


class TimestampedModel(BaseModel):
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


class IsActiveModel(BaseModel):
    """
    Abstract model with an is_active boolean field.

    Provides .active() and .inactive() queryset methods via IsActiveManager.
    """

    is_active = models.BooleanField(default=True)
    objects: managers.IsActiveManager = managers.IsActiveManager()

    class Meta:
        abstract = True


class UUIDPrimaryKeyModel(BaseModel):
    """
    Abstract model that uses UUID7 as the primary key instead of auto-increment.

    UUID7 is time-sortable, making it suitable for distributed systems while
    maintaining index efficiency.
    """

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)

    def get_id(self):
        return str(self.id)

    class Meta:
        abstract = True


class UUIDModel(BaseModel):
    """
    Abstract model that adds a unique UUID7 field alongside the default PK.

    Useful when you need a public identifier separate from the internal ID.
    """

    uuid = models.UUIDField(default=uuid7, editable=False, unique=True)

    class Meta:
        abstract = True


class SoftDeleteModel(BaseModel):
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

"""Custom Django model fields."""

from django.db import models


class NullableUniqueCharField(models.CharField):
    """
    A CharField that converts empty strings to NULL before saving.

    Useful for unique fields where you want multiple empty values to be allowed,
    since NULL values don't violate unique constraints in most databases.

    e.g.:
        email = NullableUniqueCharField(max_length=255, unique=True, blank=True, null=True)
    """

    def get_prep_value(self, value):
        if value == "":
            return None
        return value

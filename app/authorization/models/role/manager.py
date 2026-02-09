from django.db import models

from .queryset import PermissionQuerySet, RoleQuerySet


class RoleManager(models.Manager):
    def get_queryset(self):
        return RoleQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def with_permissions(self):
        return self.get_queryset().with_permissions()

    def for_user(self, user):
        return self.get_queryset().for_user(user)

    def get_by_codename(self, codename: str):
        return self.get(codename=codename)


class PermissionManager(models.Manager):
    def get_queryset(self):
        return PermissionQuerySet(self.model, using=self._db)

    def by_codename(self, codename: str):
        return self.get_queryset().by_codename(codename)

    def by_codenames(self, codenames: list[str]):
        return self.get_queryset().by_codenames(codenames)

    def get_by_codename(self, codename: str):
        return self.get(codename=codename)

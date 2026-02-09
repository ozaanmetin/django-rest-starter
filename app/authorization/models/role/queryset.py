from django.db import models


class RoleQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_permissions(self):
        return self.prefetch_related("permissions")

    def for_user(self, user):
        return self.filter(user_set=user)


class PermissionQuerySet(models.QuerySet):
    def by_codename(self, codename: str):
        return self.filter(codename=codename)

    def by_codenames(self, codenames: list[str]):
        return self.filter(codename__in=codenames)

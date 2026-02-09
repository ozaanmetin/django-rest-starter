from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionDef:
    """
    Permission definition with multi-language support.

    Usage:

    class CameraPermissions:
        GET_SNAPSHOT = PermissionDef("assets.camera.get_snapshot", {
            "en": "Get Snapshot From Camera",
            "tr": "Kameradan Anlık Görüntü Al",
        })

    In models:
        class Meta:
            permissions = [
                CameraPermissions.GET_SNAPSHOT.to_tuple(),
            ]

    In views:
        if user.has_perm(CameraPermissions.GET_SNAPSHOT.codename):
            ...
    """

    codename: str
    name: dict[str, str]

    def to_tuple(self) -> tuple[str, dict[str, str]]:
        """Convert to Django Meta.permissions format."""
        return (self.codename, self.name)

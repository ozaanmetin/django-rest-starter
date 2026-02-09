from typing import Any


class CacheKeyBuilder:
    """
    Fluent builder for constructing cache keys.
    """

    SEPERATOR = ":"
    VERSION_PREFIX = "v"

    def __init__(self, namespace: str, version: int = 1):
        """
        Builds the initial parts of the key.

        e.g.:
            builder = CacheKeyBuilder("authorization", 1)
            first part of the key: "authorization:v1"
        """
        self._parts: list[str] = [namespace, f"{self.VERSION_PREFIX}{version}"]

    def add(self, *parts: Any):
        """
        Add one or more parts to the key.

        e.g.:
            builder = CacheKeyBuilder("authorization", 1)
            builder.add("entity", user_id)
            key: "authorization:v1:entity:{user_id}"
        """
        for part in parts:
            if part is not None:
                self._parts.append(str(part))
        return self

    def build(self) -> str:
        return self.SEPERATOR.join(self._parts)

    @classmethod
    def pattern(cls, namespace: str, version: int = 1, *parts: Any) -> str:
        """
        Build a pattern for matching multiple keys.

        e.g.:
            pattern = CacheKeyBuilder.pattern("authorization", 1, "entity", "*")
            pattern: "authorization:v1:entity:*"
        """
        all_parts = [namespace, f"{cls.VERSION_PREFIX}{version}"] + list(parts)
        return cls.SEPERATOR.join(all_parts)

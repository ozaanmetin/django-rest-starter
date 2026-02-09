from typing import Any

from .backends import CacheBackend, DjangoCacheBackend
from .keys import CacheKeyBuilder


class CacheService:
    NAMESPACE = None
    VERSION = 1
    DEFAULT_TIMEOUT = 60 * 5

    def __init__(self, backend: CacheBackend[Any] = None):
        assert self.NAMESPACE is not None, "NAMESPACE must be defined in CacheService subclass"

        self.backend = backend or DjangoCacheBackend()
        # Store namespace and version for key building
        self._namespace = self.NAMESPACE
        self._version = self.VERSION

    @property
    def key_builder(self) -> type[CacheKeyBuilder]:
        """Return CacheKeyBuilder class for pattern building."""
        return CacheKeyBuilder

    def _get_key(self, *parts: Any) -> str:
        """Build a cache key with the given parts."""
        # Create fresh builder each time to avoid state accumulation
        builder = CacheKeyBuilder(self._namespace, self._version)
        return builder.add(*parts).build()

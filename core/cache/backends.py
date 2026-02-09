from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class CacheBackend(ABC, Generic[T]):
    """
    Protocol for cache backends with type-safe operations.
    """

    @abstractmethod
    def get(self, key: str) -> T | None:
        """
        Get a value from the cache.
        """
        ...

    @abstractmethod
    def set(self, key: str, value: T, timeout: int | None = None) -> bool:
        """
        Set a value in the cache.
        """
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        """
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        """
        ...

    @abstractmethod
    def clear_pattern(self, pattern: str) -> int:
        """
        Clear cache entries matching a pattern.
        """
        ...

    def get_many(self, keys: list[str]) -> dict[str, T | None]:
        return {key: self.get(key) for key in keys}

    def set_many(self, mapping: dict[str, T], timeout: int | None = None) -> bool:
        return all(self.set(key, value, timeout) for key, value in mapping.items())

    def delete_many(self, keys: list[str]) -> int:
        return sum(1 for key in keys if self.delete(key))


class DjangoCacheBackend(CacheBackend[Any]):
    """
    Django cache backend implementation.
    Uses Django's caching framework as the underlying cache.

    for settings of the cache look for
    'CACHES' in Django settings
    """

    def __init__(self, cache_alias: str = "default"):
        from django.core.cache import caches

        self._cache = caches[cache_alias]

    def get(self, key: str) -> Any | None:
        return self._cache.get(key)

    def set(self, key: str, value: Any, timeout: int | None = 300) -> bool:
        return self._cache.set(key, value, timeout)

    def delete(self, key: str) -> bool:
        return self._cache.delete(key)

    def exists(self, key: str) -> bool:
        return key in self._cache

    def clear_pattern(self, pattern: str) -> int:
        if hasattr(self._cache, "delete_pattern"):
            return self._cache.delete_pattern(pattern)
        return 0

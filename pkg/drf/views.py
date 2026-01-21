"""Base viewset classes with action-based dynamic configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework import mixins, viewsets

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission
    from rest_framework.serializers import Serializer
    from rest_framework.throttling import BaseThrottle


class BaseGenericViewSet(viewsets.GenericViewSet):
    """
    A generic viewset with dynamic resolution for serializers, permissions,
    queryset, and throttling based on the current action.

    Resolution order for serializer_class, permission_classes, throttle_classes:
        Method: get_{action}_{property}() - e.g., get_list_serializer_class()
        Attribute: {action}_{property} - e.g., list_serializer_class
        Default class attribute - e.g., serializer_class

    Resolution for queryset (method-only to avoid caching issues):
        Method: get_{action}_queryset() - e.g., get_list_queryset()
        Default: super().get_queryset()

    e.g.:
        class UserViewSet(BaseGenericViewSet):
            serializer_class = UserSerializer
            list_serializer_class = UserListSerializer

            def get_create_serializer_class(self):
                return UserCreateSerializer

            def get_list_queryset(self):
                return User.objects.select_related("profile")
    """

    def _get_action_attribute(self, attr_name: str, default):
        """Resolves attribute value based on action with fallback to default."""
        if not self.action:
            return default

        # Check for attribute: {action}_{attr_name}
        return getattr(self, f"{self.action}_{attr_name}", default)

    def _get_action_method_result(self, method_name: str):
        """Calls get_{action}_{method_name}() if it exists, returns None otherwise."""
        if not self.action:
            return None

        method = getattr(self, f"get_{self.action}_{method_name}", None)
        if callable(method):
            return method()
        return None

    def get_queryset(self):
        """Returns the queryset for the current action."""
        queryset = self._get_action_method_result("queryset")
        if queryset is not None:
            return queryset
        return super().get_queryset()

    def get_serializer_class(self) -> type[Serializer]:
        """Returns the serializer class for the current action."""
        result = self._get_action_method_result("serializer_class")
        if result is not None:
            return result
        return self._get_action_attribute("serializer_class", self.serializer_class)

    def get_permissions(self) -> list[BasePermission]:
        """Returns the permission instances for the current action."""
        result = self._get_action_method_result("permission_classes")
        if result is not None:
            permission_classes = result
        else:
            permission_classes = self._get_action_attribute("permission_classes", self.permission_classes)
        return [permission() for permission in permission_classes]

    def get_throttles(self) -> list[BaseThrottle]:
        """Returns the throttle instances for the current action."""
        result = self._get_action_method_result("throttle_classes")
        if result is not None:
            throttle_classes = result
        else:
            throttle_classes = self._get_action_attribute("throttle_classes", self.throttle_classes)
        return [throttle() for throttle in throttle_classes]


class BaseModelViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    BaseGenericViewSet,
):
    """
    A model viewset with full CRUD operations and action-based dynamic configuration.

    Inherits all mixins and dynamic resolution from BaseGenericViewSet.
    """

    pass

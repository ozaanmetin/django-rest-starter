from rest_framework import serializers


class SubErrorSerializer(serializers.Serializer):
    """Field-level error structure."""

    field = serializers.CharField(required=False, allow_null=True)
    code = serializers.CharField(required=False, allow_null=True)
    detail = serializers.CharField(required=False, allow_null=True)


class ApiResponseSerializer(serializers.Serializer):
    """Standard API response structure for documentation."""

    data = serializers.JSONField()
    detail = serializers.CharField(required=False)
    metadata = serializers.DictField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response structure for documentation."""

    code = serializers.CharField()
    detail = serializers.CharField()
    errors = SubErrorSerializer(many=True, required=False, default=[])


class PaginatedResponseSerializer(serializers.Serializer):
    """DRF PageNumberPagination response structure."""

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField(child=serializers.JSONField())


class CursorPaginatedResponseSerializer(serializers.Serializer):
    """DRF CursorPagination response structure."""

    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField(child=serializers.JSONField())


# Cache for dynamically created serializer classes
_serializer_cache: dict[str, type[serializers.Serializer]] = {}


def _get_or_create_serializer(
    cache_key: str,
    name: str,
    fields: dict,
) -> type[serializers.Serializer]:
    """Helper to get cached serializer or create new one."""
    if cache_key in _serializer_cache:
        return _serializer_cache[cache_key]

    serializer_class = type(name, (serializers.Serializer,), fields)
    _serializer_cache[cache_key] = serializer_class
    return serializer_class


def api_response_serializer(
    data_serializer: type[serializers.Serializer],
    *,
    detail: str | None = None,
    name: str | None = None,
) -> type[serializers.Serializer]:
    """
    Factory function to create a typed ApiResponseSerializer.

    Usage with drf-spectacular:
        @extend_schema(responses={200: ApiResponse.get_serializer_class(UserSerializer)})
        def get_user(request, pk):
            user = User.objects.get(pk=pk)
            return ApiResponse(data=UserSerializer(user).data).to_response()
    """
    serializer_name = name or f"{data_serializer.__name__}ApiResponse"
    cache_key = f"{serializer_name}:{detail}"

    fields = {
        "data": data_serializer(),
        "detail": serializers.CharField(required=False, default=detail)
        if detail
        else serializers.CharField(required=False),
        "metadata": serializers.DictField(required=False),
    }

    return _get_or_create_serializer(cache_key, serializer_name, fields)


def paginated_response_serializer(
    data_serializer: type[serializers.Serializer],
    *,
    name: str | None = None,
) -> type[serializers.Serializer]:
    """
    Factory function to create a typed PaginatedResponseSerializer.

    Usage with drf-spectacular:
        @extend_schema(responses={200: paginated_response_serializer(UserSerializer)})
        def list_users(request):
            ...
    """
    serializer_name = name or f"{data_serializer.__name__}PaginatedResponse"
    cache_key = f"paginated:{serializer_name}"

    fields = {
        "count": serializers.IntegerField(),
        "next": serializers.URLField(allow_null=True),
        "previous": serializers.URLField(allow_null=True),
        "results": serializers.ListSerializer(child=data_serializer()),
    }

    return _get_or_create_serializer(cache_key, serializer_name, fields)


def cursor_paginated_response_serializer(
    data_serializer: type[serializers.Serializer],
    *,
    name: str | None = None,
) -> type[serializers.Serializer]:
    """
    Factory function to create a typed CursorPaginatedResponseSerializer.

    Usage with drf-spectacular:
        @extend_schema(responses={200: cursor_paginated_response_serializer(UserSerializer)})
        def list_users(request):
            ...
    """
    serializer_name = name or f"{data_serializer.__name__}CursorPaginatedResponse"
    cache_key = f"cursor_paginated:{serializer_name}"

    fields = {
        "next": serializers.URLField(allow_null=True),
        "previous": serializers.URLField(allow_null=True),
        "results": serializers.ListSerializer(child=data_serializer()),
    }

    return _get_or_create_serializer(cache_key, serializer_name, fields)


def error_response_serializer(
    *,
    code: str | None = None,
    detail: str | None = None,
    name: str | None = None,
) -> type[serializers.Serializer]:
    """
    Factory function to create a typed ErrorResponseSerializer.

    Usage with drf-spectacular:
        @extend_schema(responses={400: ErrorResponse.get_serializer_class(code="validation_error")})
        def create_user(request):
            ...
    """
    serializer_name = name or "ErrorResponse"
    cache_key = f"error:{serializer_name}:{code}:{detail}"

    fields = {
        "code": serializers.CharField(default=code) if code else serializers.CharField(),
        "detail": serializers.CharField(default=detail) if detail else serializers.CharField(),
        "errors": SubErrorSerializer(many=True, required=False, default=[]),
    }

    return _get_or_create_serializer(cache_key, serializer_name, fields)

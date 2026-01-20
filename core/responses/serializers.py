from rest_framework import serializers


class SubErrorSerializer(serializers.Serializer):
    """Field-level error structure."""
    field = serializers.CharField(required=False, allow_null=True)
    code = serializers.CharField(required=False, allow_null=True)
    detail = serializers.CharField(required=False, allow_null=True)


class PaginationSerializer(serializers.Serializer):
    """Pagination metadata structure."""
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)


class ApiResponseSerializer(serializers.Serializer):
    """Standard API response structure for documentation."""
    data = serializers.JSONField()
    detail = serializers.CharField(required=False)
    metadata = serializers.DictField(required=False)


class PaginatedApiResponseSerializer(serializers.Serializer):
    """Paginated API response structure for documentation."""
    data = serializers.ListField(child=serializers.JSONField())
    pagination = PaginationSerializer()
    detail = serializers.CharField(required=False)
    metadata = serializers.DictField(required=False)


class ErrorResponseSerializer(serializers.Serializer):
    """Standard error response structure for documentation."""
    code = serializers.CharField()
    detail = serializers.CharField()
    errors = SubErrorSerializer(many=True, required=False)

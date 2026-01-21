from datetime import datetime
from typing import Any

from rest_framework import serializers, status
from rest_framework.response import Response


class ApiResponse:
    """Helper class to build standardized API responses."""

    def __init__(
        self,
        data: Any,
        detail: str | None = None,
        metadata: dict | None = None,
    ):
        self.data = data
        self.detail = detail
        self.metadata = metadata

    def to_dict(self) -> dict:
        result = {"data": self.data}

        if self.detail is not None:
            result["detail"] = self.detail

        if self.metadata is not None:
            result["metadata"] = self.metadata

        return result

    def to_response(self, status_code: int = status.HTTP_200_OK) -> Response:
        return Response(self.to_dict(), status=status_code)

    @classmethod
    def with_timestamp(cls, data: Any, **kwargs) -> "ApiResponse":
        metadata = kwargs.pop("metadata", {}) or {}
        metadata["timestamp"] = datetime.now().isoformat()
        return cls(data=data, metadata=metadata, **kwargs)

    @classmethod
    def get_serializer_class(
        cls,
        data_serializer: type[serializers.Serializer],
        *,
        detail: str | None = None,
        name: str | None = None,
    ) -> type[serializers.Serializer]:
        """Get a serializer class for this response type."""
        from .serializers import api_response_serializer

        return api_response_serializer(data_serializer, detail=detail, name=name)


class ErrorResponse:
    """Helper class to build standardized error responses."""

    def __init__(
        self,
        code: str,
        detail: str,
        errors: list[dict] | None = None,
    ):
        self.code = code
        self.detail = detail
        self.errors = errors

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "detail": self.detail,
            "errors": self.errors or [],
        }

    def to_response(self, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
        return Response(self.to_dict(), status=status_code)

    @classmethod
    def get_serializer_class(
        cls,
        *,
        code: str | None = None,
        detail: str | None = None,
        name: str | None = None,
    ) -> type[serializers.Serializer]:
        """Get a serializer class for this response type."""
        from .serializers import error_response_serializer

        return error_response_serializer(code=code, detail=detail, name=name)


class SubError:
    """Helper class to build field-level errors."""

    def __init__(
        self,
        field: str | None = None,
        code: str | None = None,
        detail: str | None = None,
    ):
        self.field = field
        self.code = code
        self.detail = detail

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "code": self.code,
            "detail": self.detail,
        }


def sub_error(
    field: str | None = None,
    code: str | None = None,
    detail: str | None = None,
) -> dict:
    """Helper to create SubError dict."""
    return SubError(field=field, code=code, detail=detail).to_dict()

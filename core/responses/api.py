from datetime import datetime
from typing import Any, Optional

from rest_framework import status
from rest_framework.response import Response


class ApiResponse:
    """Helper class to build standardized API responses."""

    def __init__(
        self,
        data: Any,
        detail: Optional[str] = None,
        metadata: Optional[dict] = None,
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


class PaginatedApiResponse:
    """Helper class to build standardized paginated API responses."""

    def __init__(
        self,
        data: list,
        count: int,
        page: int,
        page_size: int,
        total_pages: int,
        next_url: Optional[str] = None,
        previous_url: Optional[str] = None,
        detail: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        self.data = data
        self.count = count
        self.page = page
        self.page_size = page_size
        self.total_pages = total_pages
        self.next_url = next_url
        self.previous_url = previous_url
        self.detail = detail
        self.metadata = metadata

    def to_dict(self) -> dict:
        result = {
            "data": self.data,
            "pagination": {
                "count": self.count,
                "page": self.page,
                "page_size": self.page_size,
                "total_pages": self.total_pages,
                "next": self.next_url,
                "previous": self.previous_url,
            },
        }

        if self.detail is not None:
            result["detail"] = self.detail

        if self.metadata is not None:
            result["metadata"] = self.metadata

        return result

    def to_response(self, status_code: int = status.HTTP_200_OK) -> Response:
        return Response(self.to_dict(), status=status_code)


class ErrorResponse:
    """Helper class to build standardized error responses."""

    def __init__(
        self,
        code: str,
        detail: str,
        errors: Optional[list[dict]] = None,
    ):
        self.code = code
        self.detail = detail
        self.errors = errors

    def to_dict(self) -> dict:
        result = {
            "code": self.code,
            "detail": self.detail,
        }

        if self.errors is not None:
            result["errors"] = self.errors

        return result

    def to_response(self, status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
        return Response(self.to_dict(), status=status_code)


def sub_error(
    field: Optional[str] = None,
    code: Optional[str] = None,
    detail: Optional[str] = None,
) -> dict:
    """Helper to create SubError dict."""
    result = {}
    if field is not None:
        result["field"] = field
    if code is not None:
        result["code"] = code
    if detail is not None:
        result["detail"] = detail
    return result

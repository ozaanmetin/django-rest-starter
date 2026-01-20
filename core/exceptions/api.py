from typing import Optional

from rest_framework.exceptions import APIException
from rest_framework import status


class BaseAPIException(APIException):
    """
    Base exception that returns ErrorResponse format.

    Usage:
        raise BaseAPIException(
            code="user_not_found",
            detail="User with this ID does not exist",
            status_code=404
        )

        raise BaseAPIException(
            code="validation_error",
            detail="Validation failed",
            errors=[
                sub_error("email", "invalid", "Invalid email format"),
                sub_error("password", "min_length", "Password too short")
            ]
        )
    """

    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "error"
    default_detail = "An error occurred"

    def __init__(
        self,
        code: Optional[str] = None,
        detail: Optional[str] = None,
        errors: Optional[list[dict]] = None,
        status_code: Optional[int] = None,
    ):
        self.code = code or self.default_code
        self.detail = detail or self.default_detail
        self.errors = errors

        if status_code is not None:
            self.status_code = status_code

        super().__init__(detail=self.detail, code=self.code)


class NotFoundError(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "not_found"
    default_detail = "Resource not found"


class ValidationError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "validation_error"
    default_detail = "Validation failed"


class UnauthorizedError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = "unauthorized"
    default_detail = "Authentication required"


class ForbiddenError(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = "forbidden"
    default_detail = "Permission denied"


class ConflictError(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "conflict"
    default_detail = "Resource conflict"

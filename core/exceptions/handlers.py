"""
Custom Exception Handler for DRF

DRF (Django REST Framework) returns exceptions in different formats:
- ValidationError: {"field_name": ["error1", "error2"]} or {"field_name": "error"}
- AuthenticationFailed/JWT: {"detail": "...", "code": "...", "messages": [...]}
- PermissionDenied: {"detail": "..."}
- NotFound: {"detail": "..."}

This handler catches all these formats and converts them to a consistent ErrorResponse format.

Additionally, DRF returns error messages as ErrorDetail objects. These objects
can appear as "ErrorDetail(string='...', code='...')" when converted with str().
This handler also converts these objects to clean strings.
"""

from rest_framework.views import exception_handler

from core.responses import ErrorResponse, sub_error

from .api import BaseAPIException

# Special keys used by DRF for non-field errors.
# If these keys are present, it's not a field validation error,
# but a general error like authentication/authorization.
# e.g.: JWT token error {"detail": "Token expired", "code": "token_not_valid", "messages": [...]}
_NON_FIELD_ERROR_KEYS = {"detail", "code", "messages"}


def _get_error_code(value, default="invalid"):
    """
    Extract error code from DRF ErrorDetail object.

    DRF returns error messages as ErrorDetail objects.
    These objects have a .code attribute ("required", "invalid", "token_not_valid").
    """
    if hasattr(value, "code") and value.code:
        return str(value.code)
    return default


def _to_string(value):
    """
    Convert value to a clean string.

    DRF's ErrorDetail objects can sometimes appear as
    "ErrorDetail(string='...', code='...')" when converted with str().
    This function also recursively cleans nested dict/list structures.
    """
    if isinstance(value, dict):
        return str({k: _to_string(v) for k, v in value.items()})
    if isinstance(value, list):
        return str([_to_string(item) for item in value])
    return str(value)


def custom_exception_handler(exc, context):
    """
    Convert DRF exceptions to a consistent ErrorResponse format.

    Response Format:
    {
        "code": "error_code",
        "detail": "Human readable message",
        "errors": [...]  # Only for validation errors
    }
    """
    # Call DRF's default handler - returns None if exception is not handled
    response = exception_handler(exc, context)

    if response is None:
        return None

    # Our custom exceptions are already in the correct format
    if isinstance(exc, BaseAPIException):
        error_response = ErrorResponse(
            code=exc.code,
            detail=exc.detail,
            errors=exc.errors,
        )
        response.data = error_response.to_dict()
        return response

    # DRF returns errors in dict format
    # Two types of dict are possible:
    # 1. Field validation: {"username": ["This field is required"], "email": ["Invalid email"]}
    # 2. Non-field error: {"detail": "Token expired", "code": "token_not_valid"}
    if hasattr(exc, "detail") and isinstance(exc.detail, dict):
        keys = set(exc.detail.keys())

        # Non-field error check (JWT, auth errors, etc.)
        # If all keys are special keys, this is not a field validation error
        if keys.issubset(_NON_FIELD_ERROR_KEYS):
            detail = _to_string(exc.detail.get("detail", "An error occurred"))
            code = _get_error_code(
                exc.detail.get("code"),
                default=getattr(exc, "default_code", "error"),
            )
            response.data = ErrorResponse(code=code, detail=detail).to_dict()
            return response

        # Field validation errors - create sub_error for each field
        sub_errors = []
        for field, errors in exc.detail.items():
            # DRF sometimes returns a list, sometimes a single value
            errors_list = errors if isinstance(errors, list) else [errors]
            for error in errors_list:
                sub_errors.append(
                    sub_error(
                        field=field,
                        code=_get_error_code(error),
                        detail=_to_string(error),
                    )
                )

        response.data = ErrorResponse(
            code="validation_error",
            detail="Validation failed",
            errors=sub_errors or None,
        ).to_dict()
        return response

    # DRF sometimes returns errors in list format (e.g., non_field_errors)
    if hasattr(exc, "detail") and isinstance(exc.detail, list):
        detail = ", ".join(_to_string(e) for e in exc.detail)
        code = getattr(exc, "default_code", "error")
        response.data = ErrorResponse(code=code, detail=detail).to_dict()
        return response

    # Simple string errors (PermissionDenied, NotFound, etc.)
    detail = _to_string(exc.detail) if hasattr(exc, "detail") else str(exc)
    code = getattr(exc, "default_code", "error")
    response.data = ErrorResponse(code=code, detail=detail).to_dict()

    return response

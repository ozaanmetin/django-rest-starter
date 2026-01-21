from rest_framework.views import exception_handler

from core.responses import ErrorResponse, sub_error

from .api import BaseAPIException


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    # Handle our custom BaseAPIException
    if isinstance(exc, BaseAPIException):
        error_response = ErrorResponse(
            code=exc.code,
            detail=exc.detail,
            errors=exc.errors,
        )
        response.data = error_response.to_dict()
        return response

    # Handle DRF validation errors (dict format)
    if hasattr(exc, "detail") and isinstance(exc.detail, dict):
        sub_errors = []
        for field_name, errors in exc.detail.items():
            if isinstance(errors, list):
                for error in errors:
                    error_code = getattr(error, "code", "invalid") if hasattr(error, "code") else "invalid"
                    sub_errors.append(sub_error(field=field_name, code=error_code, detail=str(error)))
            else:
                error_code = getattr(errors, "code", "invalid") if hasattr(errors, "code") else "invalid"
                sub_errors.append(sub_error(field=field_name, code=error_code, detail=str(errors)))

        error_response = ErrorResponse(
            code="validation_error",
            detail="Validation failed",
            errors=sub_errors if sub_errors else None,
        )
        response.data = error_response.to_dict()
        return response

    # Handle DRF list errors
    if hasattr(exc, "detail") and isinstance(exc.detail, list):
        error_response = ErrorResponse(
            code=getattr(exc, "default_code", "error"),
            detail=", ".join(str(e) for e in exc.detail),
        )
        response.data = error_response.to_dict()
        return response

    # Handle simple DRF errors
    detail = str(exc.detail) if hasattr(exc, "detail") else str(exc)
    code = getattr(exc, "default_code", "error")

    error_response = ErrorResponse(code=code, detail=detail)
    response.data = error_response.to_dict()

    return response

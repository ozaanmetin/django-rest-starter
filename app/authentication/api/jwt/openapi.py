from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status

from core.responses.serializers import error_response_serializer

from .serializers import (
    RefreshTokenSerializer,
    SignInSerializer,
    SignOutSerializer,
    VerifyTokenSerializer,
)

# Tags

JWT_TAG = ["Authentication - Jwt"]


# Response Serializers

UnauthorizedErrorResponse = error_response_serializer(
    code="unauthorized",
    detail="No active account found with the given credentials",
    name="UnauthorizedErrorResponse",
)

TokenExpiredErrorResponse = error_response_serializer(
    code="unauthorized",
    detail="Token is invalid or expired",
    name="TokenExpiredErrorResponse",
)

InvalidTokenErrorResponse = error_response_serializer(
    code="invalid_token",
    detail="Token is invalid or expired",
    name="InvalidTokenErrorResponse",
)


# Schema Decorators

sign_in_schema = extend_schema(
    description="""
    Authenticate user and obtain JWT token pair.

    Returns access and refresh tokens upon successful authentication.
    The access token is short-lived (default: 5 minutes) and should be
    used for API authentication. The refresh token is long-lived
    (default: 30 days) and can be used to obtain new access tokens.
    """,
    tags=JWT_TAG,
    request=SignInSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=RefreshTokenSerializer),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=UnauthorizedErrorResponse),
    },
)

refresh_token_schema = extend_schema(
    description="""
    Obtain a new access token using a valid refresh token.

    If token rotation is enabled, a new refresh token will also be
    returned and the old one will be blacklisted.
    """,
    tags=JWT_TAG,
    request=RefreshTokenSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=RefreshTokenSerializer),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=TokenExpiredErrorResponse),
    },
)

verify_token_schema = extend_schema(
    description="""
    Verify the validity of a JWT token.

    Returns empty response if token is valid, error otherwise.
    """,
    tags=JWT_TAG,
    request=VerifyTokenSerializer,
    responses={
        status.HTTP_200_OK: OpenApiResponse(),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=TokenExpiredErrorResponse),
    },
)

sign_out_schema = extend_schema(
    description="""
    Sign out user by blacklisting the refresh token.

    After sign out, the refresh token can no longer be used to obtain
    new access tokens. The access token will remain valid until it
    expires.
    """,
    tags=JWT_TAG,
    request=SignOutSerializer,
    responses={
        status.HTTP_204_NO_CONTENT: OpenApiResponse(),
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=InvalidTokenErrorResponse),
    },
)

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status

from core.responses.serializers import error_response_serializer

from .serializers import UserMeSerializer

# Tags

USERS_TAG = ["Accounts - Users"]


# Error Response Serializers

UnauthorizedErrorResponse = error_response_serializer(
    code="unauthorized",
    detail="Authentication credentials were not provided.",
    name="UserUnauthorizedErrorResponse",
)


# Schema Decorators

user_me_schema = extend_schema(
    operation_id="user_me",
    summary="Get Current User",
    description="Returns the authenticated user's profile information.",
    tags=USERS_TAG,
    responses={
        status.HTTP_200_OK: OpenApiResponse(response=UserMeSerializer),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(response=UnauthorizedErrorResponse),
    },
)

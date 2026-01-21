from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .openapi import (
    sign_in_schema,
    refresh_token_schema,
    verify_token_schema,
    sign_out_schema,
)
from .serializers import (
    SignInSerializer,
    RefreshTokenSerializer,
    SignOutSerializer,
    VerifyTokenSerializer,
)
from .throttles import (
    SignInThrottle,
    RefreshTokenThrottle,
    VerifyTokenThrottle,
    SignOutThrottle,
)


@sign_in_schema
class SignInView(TokenObtainPairView):
    """API view to obtain JWT token pair (access and refresh tokens)."""

    permission_classes = [AllowAny]
    throttle_classes = [SignInThrottle]
    serializer_class = SignInSerializer


@refresh_token_schema
class RefreshTokenView(TokenRefreshView):
    """API view to refresh JWT access token using a valid refresh token."""

    permission_classes = [AllowAny]
    throttle_classes = [RefreshTokenThrottle]
    serializer_class = RefreshTokenSerializer


@verify_token_schema
class VerifyTokenView(TokenVerifyView):
    """API view to verify the validity of a JWT token."""

    permission_classes = [AllowAny]
    throttle_classes = [VerifyTokenThrottle]
    serializer_class = VerifyTokenSerializer


@sign_out_schema
class SignOutView(GenericAPIView):
    """API view to handle user sign out by blacklisting the refresh token."""

    permission_classes = [AllowAny]
    throttle_classes = [SignOutThrottle]
    serializer_class = SignOutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

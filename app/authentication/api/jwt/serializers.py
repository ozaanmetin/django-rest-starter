"""
JWT serializers for authentication.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenVerifySerializer,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from core.exceptions import UnauthorizedError, ValidationError


class SignInSerializer(TokenObtainPairSerializer):
    """
    Serializer JWT token obtain pair (sign in) endpoint.
    """

    default_error_messages = {"no_active_account": _("No active account found with the given credentials")}

    @classmethod
    def get_token(cls, user):
        """
        Override to customize token claims.
        """
        return super().get_token(user)

    def validate(self, attrs):
        """
        Override to add custom validation logic.
        """
        return super().validate(attrs)


class RefreshTokenSerializer(TokenRefreshSerializer):
    """
    Serializer for refreshing JWT tokens.
    """

    default_error_messages = {"no_active_account": _("No active account found with the given credentials")}

    def validate(self, attrs):
        """
        Same implementation of TokenRefreshSerializer but
        with added user existence and can_authenticate checks.
        """

        refresh = self.token_class(attrs["refresh"])

        user_id = refresh.payload.get(api_settings.USER_ID_CLAIM, None)

        if user_id:
            try:
                user = get_user_model().objects.get(**{api_settings.USER_ID_FIELD: user_id})

                # Check if user can sign in and passes authentication rules
                if not user.can_authenticate or not api_settings.USER_AUTHENTICATION_RULE(user):
                    raise UnauthorizedError(
                        self.error_messages["no_active_account"],
                        "no_active_account",
                    )

            except ObjectDoesNotExist as err:
                # User doesn't exist
                raise UnauthorizedError(
                    self.error_messages["no_active_account"],
                    "no_active_account",
                ) from err

        # If we get here, user exists and can sign in, proceed with token refresh
        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()
            refresh.outstand()

            data["refresh"] = str(refresh)

        return data


class VerifyTokenSerializer(TokenVerifySerializer):
    """
    Serializer for verifying JWT tokens.
    """

    def validate(self, attrs):
        """
        Override to add custom validation logic.
        """
        return super().validate(attrs)


class SignOutSerializer(serializers.Serializer):
    """
    Serializer for signing out by blacklisting the refresh token.
    """

    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()
        except TokenError as e:
            raise ValidationError(
                detail=_("Token is invalid or expired"),
                code="invalid_token",
            ) from e
        except Exception as e:
            raise ValidationError(
                detail=_("An error occurred while blacklisting the token"),
                code="sign_out_error",
            ) from e

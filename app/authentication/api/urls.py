from django.urls import path, include
from rest_framework.routers import DefaultRouter

# jwt views
from .jwt.views import (
    SignInView,
    RefreshTokenView,
    VerifyTokenView,
    SignOutView,
)

app_name = "authentication"

router = DefaultRouter()

urlpatterns = [
    path("", include(router.urls)),
    path("sign-in/", SignInView.as_view(), name="sign-in"),
    path("refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("verify/", VerifyTokenView.as_view(), name="token-verify"),
    path("sign-out/", SignOutView.as_view(), name="sign-out"),
]

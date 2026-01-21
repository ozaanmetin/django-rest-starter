"""
API v1 URL Configuration.

All v1 API routes are registered here.
"""

from django.urls import path, include

app_name = "api-v1"

urlpatterns = [
    path("auth/", include("app.authentication.api.urls")),
    path("accounts/", include("app.accounts.api.urls")),
]

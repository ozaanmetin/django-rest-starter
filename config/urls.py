"""
URL configuration for config project.
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def home_page(request):
    # redirect to login
    return redirect("admin:login")


# openapi schema views
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # root
    path("", home_page, name="home"),
    # admin
    path("mgmt/", admin.site.urls),
    # api
    path("api/v1/", include("config.api.v1.urls")),
    # docs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

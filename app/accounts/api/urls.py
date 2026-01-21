from django.urls import path

from .user.views import UserMeView

app_name = "accounts"

urlpatterns = [
    path("me/", UserMeView.as_view(), name="user-me"),
]

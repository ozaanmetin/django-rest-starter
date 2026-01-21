from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .openapi import user_me_schema
from .serializers import UserMeSerializer
from .throttles import UserMeThrottle


@user_me_schema
class UserMeView(RetrieveAPIView):
    """Returns the authenticated user's profile information."""

    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserMeThrottle]

    def get_object(self):
        return self.request.user

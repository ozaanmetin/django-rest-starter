from rest_framework import serializers

from app.accounts.models import User


class UserMeSerializer(serializers.ModelSerializer):
    """Serializer for current user's profile information."""

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "date_joined",
            "last_login",
        ]
        read_only_fields = fields

from rest_framework import serializers

from .models import User


class TinyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name", "avatar", "username")


class PrivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = "__all__"
        # 제외하기 exclude
        exclude = (
            "password",
            "is_superuser",
            "id",
            "is_staff",
            "is_active",
            "first_name",
            "last_name",
            "groups",
            "user_permissions",
        )

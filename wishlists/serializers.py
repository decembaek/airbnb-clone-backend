from rest_framework import serializers

from .models import WishList
from rooms.serializers import RoomListSerializer


class WishlistSerializer(serializers.ModelSerializer):
    rooms = RoomListSerializer(many=True, read_only=True)

    class Meta:
        model = WishList
        fields = (
            "pk",
            "name",
            "rooms",
        )

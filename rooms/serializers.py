from rest_framework.serializers import ModelSerializer
from .models import Amenity, Room
from users.serializers import TinyUserSerializer
from categories.serializers import CategorySerializer

# class RoomSerializer(ModelSerializer):
#     class Meta:
#         model = Room
#         fields = "__all__"
#         depth = 1


class AmenitySerializer(ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"
        # fields = (
        #     # "name",
        #     # "description",
        #     "__all__",
        # )


class RoomDetailSerializer(ModelSerializer):
    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Room
        fields = "__all__"

    # def create(self, validated_data):
    #     print(validated_data)
    #     return
    # return Room.objects.create(**validated_data)


class RoomListSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
        )

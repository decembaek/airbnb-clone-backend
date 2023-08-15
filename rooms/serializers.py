from rest_framework import serializers

from .models import Amenity, Room

from users.serializers import TinyUserSerializer
from categories.serializers import CategorySerializer
from reviews.serializers import ReviewSerializer


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        # fields = "__all__"
        fields = (
            "name",
            "description",
        )


class RoomDetailSerializer(serializers.ModelSerializer):
    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    # 역접근자
    # reviews = ReviewSerializer(many=True, read_only=True)

    # 사용할려면 get_{method}
    rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = "__all__"
        # depth = 1

    # method 이름은 get_위에 있는 메소드로 적어야함
    def get_rating(self, room):
        return room.rating()  # def rating -> Room 모델에 정의한 함수

    def get_is_owner(self, room):
        request = self.context["request"]  # view 함수에서 context 받을수 있음
        return room.owner == request.user

    # def create(self, validated_data):  # 삭제예정 일부터 고장내기
    #     return


class RoomListSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = (
            "pk",
            "name",
            "country",
            "city",
            "price",
            "rating",
            "is_owner",
        )
        # depth = 1

    def get_rating(self, room):
        return room.rating()

    def get_is_owner(self, room):
        request = self.context["request"]  # view 함수에서 context 받을수 있음
        return room.owner == request.user

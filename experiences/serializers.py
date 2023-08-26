from rest_framework.serializers import ModelSerializer
from .models import Perk, Experience
from users.serializers import TinyUserSerializer


class PerkSerializer(ModelSerializer):
    class Meta:
        model = Perk
        fields = "__all__"


class ExperiencesSerializer(ModelSerializer):
    host = TinyUserSerializer(read_only=True)
    perks = PerkSerializer(many=True, read_only=True)

    class Meta:
        model = Experience
        fields = "__all__"

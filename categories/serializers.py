from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category

        # 보여줄 필드    __all__ 할시 전부 공개
        fields = (
            "pk",
            "name",
            "kind",
        )
        # exclude 제외시키기
        # exclude = (
        #     "create_dat"
        # )

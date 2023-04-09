from django.contrib import admin
from .models import House

# Register your models here.


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = (  # admin 에서 보이는 열(세로) 종류
        "name",
        "price_per_night",
        "address",
        "pets_allowed",
    )
    list_filter = (  # admin 에서 오른쪽 필터 기능
        "price_per_night",
        "pets_allowed",
    )
    search_fields = ("address",)  # 검색 기능
    list_display_links = (
        "name",
        "address",
    )  # 링크 들어가는 필드

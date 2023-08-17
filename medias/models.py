from django.db import models
from common.models import CommonModel

# Create your models here.


class Photo(CommonModel):
    # file = models.ImageField()  # 파일 보안상 다른 서버에서 파일 URL 받는게 안전함
    file = models.URLField()
    description = models.CharField(
        max_length=140,
    )
    room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="photos",
    )
    experience = models.ForeignKey(
        "experiences.Experience",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="photos",
    )

    def __str__(self) -> str:
        return "Photo File"


class Video(CommonModel):
    # file = models.FileField()  # 파일 보안상 다른 서버에서 파일 URL 받는게 안전함
    file = models.URLField()
    experience = models.OneToOneField(
        "experiences.Experience",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return "Video File"

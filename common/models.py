from django.db import models


# Create your models here.
class CommonModel(models.Model):

    """Common Model Definition"""

    created_at = models.DateTimeField(auto_now_add=True)  # 처음 만들어질떄 시간
    updated_at = models.DateTimeField(auto_now=True)  # update time

    class Meta:
        abstract = True  # 이 모델은 데이터베이스에 올리지 않음

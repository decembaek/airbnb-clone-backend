from django.db import models

# Create your models here.
class House(models.Model):
    """Model Definetion HOUSE MODEL"""

    name = models.CharField(max_length=140) #텍스트 글자 수 제한을 걸떄 사용
    price_per_night = models.PositiveIntegerField(verbose_name="Price", help_text="금액") # 양수의 정수
    description = models.TextField()    # Charfield 보다 긴 텍스트
    address = models.CharField(max_length=140)
    pets_allowed = models.BooleanField(
        verbose_name="Pets allowed?",
        default=True,
        help_text="Does this house allow pets?")  # BooleanField 는 True, False 두가지 경우에 사용 

    def __str__(self):
        return self.name
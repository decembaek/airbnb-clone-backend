from django.utils import timezone

from rest_framework import serializers

from .models import Booking


class CreateRoomBookingSerializer(serializers.ModelSerializer):
    # DB에선 null, blank True 지만 필수로 하기 위해 제작
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    class Meta:
        model = Booking
        fields = ("check_in", "check_out", "guests")

    # 특정 필드의 검증이 필요할경우 validate 사용 validate_필드이름
    def validate_check_in(self, value):
        # serializers.DateField로 필드 정의했기 때문에 date타입으로 넘어옴
        now = timezone.localtime(timezone.now()).date()  # 현재 시간 Date날짜만
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        return value

    def validate_check_out(self, value):
        # serializers.DateField로 필드 정의했기 때문에 date타입으로 넘어옴
        now = timezone.localtime(timezone.now()).date()  # 현재 시간 Date날짜만
        if now > value:
            raise serializers.ValidationError("Can't book in the past!")
        return value

    # validate 전체 검증, 예약시간 겹치지 않는지확인하기
    def validate(self, data):
        if data["check_out"] <= data["check_in"]:
            raise serializers.ValidationError("check out이 check in보다 짫아")

        # 크거나 같을때 __gte 작거나 같을때 __lte (중요) 예약할때 중요한 알고리즘
        if Booking.objects.filter(
            check_in__lte=data["check_out"],
            check_out__gte=data["check_in"],
        ).exists():  # True면 데이터가 있는거임
            raise serializers.ValidationError("이미 예약된 날짜거나 예약할수없습니다.")
        return data


class PublicBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            "pk",
            "check_in",
            "check_out",
            "experience_time",
            "guests",
        )

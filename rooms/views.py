from django.db import transaction  # 모든 변경사항 중 1개 실패하면 전체 되돌리기
from django.conf import settings  # Django settings.py 가져오기
from django.utils import timezone  # Django 시간 타임존 사용하는법

from rest_framework.views import APIView
from rest_framework.exceptions import (
    NotFound,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Amenity, Room
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer

from categories.models import Category
from bookings.models import Booking

from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer
from bookings.serialziers import PublicBookingSerializer, CreateRoomBookingSerializer


# /api/v1/rooms/amenities


class Amenities(APIView):
    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(AmenitySerializer(amenity).data)
        else:
            return Response(serializer.errors)


class AmenitiesDetail(APIView):
    def get_object(self, pk):
        try:
            return Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data)

    def put(self, request, pk):
        amenity = self.get_object(pk)
        serializer = AmenitySerializer(
            amenity,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_amenity = serializer.save()
            return Response(AmenitySerializer(updated_amenity).data)
        else:
            return Response

    def delete(self, request, pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class Rooms(APIView):
    #  if user.id_authenticated 같은 코드줄 대신 사용가능
    permission_classes = [IsAuthenticatedOrReadOnly]  # 권한 문제 해결

    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(
            all_rooms,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_authenticated:  # 유저 인증
            serializer = RoomDetailSerializer(data=request.data)
            if serializer.is_valid():
                category_pk = request.data.get("category")
                if not category_pk:
                    raise ParseError(
                        "Category is required"
                    )  # 400 Bad Request 에러 메세지 입력가능
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                        raise ParseError("The category kind should be rooms")
                except Category.DoesNotExist:
                    raise ParseError("Category None")  # 400 Bad Request
                try:
                    with transaction.atomic():  # 실패시 변경사항 되돌리기
                        room = serializer.save(
                            owner=request.user,
                            category=category,
                        )
                        amenities = request.data.get("amenities")
                        # ManyToMany 필드는 모델 생성 후 model.filed.add(추가요소) 해야함 .remove 로 삭제도 가능
                        for amenity_pk in amenities:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            room.amenities.add(amenity)
                        # try:
                        #     amenity = Amenity.objects.get(pk=amenity_pk)
                        #     room.amenities.add(amenity)
                        # except Amenity.DoesNotExist:
                        #     pass
                        #  raise ParseError(f"Amenity with id {amenity_pk} not found")
                        serializer = RoomDetailSerializer(
                            room, context={"request": request}
                        )
                        return Response(serializer.data)
                except Exception as e:
                    print(e)
                    raise ParseError("Amenity not found")
            else:
                return Response(serializer.errors)
        else:
            raise NotAuthenticated


class RoomDetail(APIView):
    def get_object(self, pk):
        try:
            room = Room.objects.get(pk=pk)
            return room
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(
            room,
            context={"request": request},
        )
        return Response(serializer.data)

    def put(self, request, pk):
        room = self.get_object(pk=pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated  # Auth 회원정보 관련 에러
        if room.owner != request.user:
            raise PermissionDenied  # 권한이 없다라고 에러띄움
        serializer = RoomDetailSerializer(
            room,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            category_pk = request.data.get("category")
            if category_pk:
                try:
                    category = Category.objects.get(pk=category_pk)
                    if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                        raise ParseError("The category kind should be rooms")
                except Category.DoesNotExist:
                    raise ParseError("Category not found")
            try:
                with transaction.atomic():
                    if category_pk:
                        room = serializer.save(category=category)
                    else:
                        room = serializer.save()
                    amenities = request.data.get("amenities")
                    if amenities:
                        room.amenities.clear()
                        for amenity_pk in amenities:
                            amenity = Amenity.objects.get(pk=amenity_pk)
                            room.amenities.add(amenity)
                    return Response(RoomDetailSerializer(room).data)
            except Exception as e:
                raise ParseError("amenity not found")
            # room = serializer.save()
            # serializer = RoomDetailSerializer(room)
            # return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        room = self.get_object(pk=pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated  # Auth 회원정보 관련 에러
        if room.owner != request.user:
            raise PermissionDenied  # 권한이 없다라고 에러띄움
        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class RoomReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            room = Room.objects.get(pk=pk)
            return room
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)  # ?page=3   <- 이 값을 받음
            page = int(page)
            if page == 0:
                page = 1
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk=pk)

        # 모든 데이터를 불러오고 인덱스로 자르는게 아닌 인덱스도 같이 요청을 보내 DB 요청이 안정화됌
        reviews = room.reviews.all()[start:end]  # model.py related_name 참조
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                room=self.get_object(pk=pk),
            )
            serializer = ReviewSerializer(review)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


# 리뷰말고 amenity 도 따로 개발하기 room/id/amenities
class RoomAmenities(APIView):
    def get_object(self, pk):
        try:
            room = Room.objects.get(pk=pk)
            return room
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
            if page == 0:
                page = 1
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE
        start = (page - 1) * page_size
        end = start + page_size
        room = self.get_object(pk=pk)

        amenities = room.amenities.all()[start:end]
        serializer = AmenitySerializer(amenities, many=True)
        return Response(serializer.data)


class RoomPhotos(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def post(self, request, pk):
        room = self.get_object(pk=pk)
        if not request.user.is_authenticated:
            raise NotAuthenticated
        if request.user != room.owner:
            raise PermissionDenied  # 권한없을때 보내는 오류
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.save(room=room)
            serializer = PhotoSerializer(photo)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class RoomBookings(APIView):
    # login 안하면 read(get)만 가능
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk=pk)
        now = timezone.localtime(timezone.now())  # 현재 서버 로컬 시간 측정
        now = now.date()  # date 정보만 받기
        bookings = Booking.objects.filter(
            room=room,
            kind=Booking.BookingKindChoices.ROOM,
            check_in__gt=now,  # 현재시간보다 나중인것만 filter하기
        )
        # bookings = Booking.objects.filter(room__pk=pk) 같은 방법
        serializer = PublicBookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        room = self.get_object(pk=pk)
        serializer = CreateRoomBookingSerializer(data=request.data)
        if serializer.is_valid():
            # custom 1번 방법, 2번은 serializers.py 에서 validate 설정
            # check_in = request.data.get("check_in")
            booking = serializer.save(
                room=room,
                user=request.user,
                kind=Booking.BookingKindChoices.ROOM,
            )
            serializer = PublicBookingSerializer(booking)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

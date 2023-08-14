from django.db import transaction  # 모든 변경사항 중 1개 실패하면 전체 되돌리기

from rest_framework.views import APIView
from rest_framework.exceptions import (
    NotFound,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
)
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from categories.models import Category
from .models import Amenity, Room
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer


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
                        serializer = RoomDetailSerializer(room)
                        return Response(serializer.data)
                except Exception:
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
        print(request.data)
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
